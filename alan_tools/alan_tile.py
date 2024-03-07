'''
Class and associated functions for generating artificial light at night under
the sea data.

'''
from pathlib import Path
from datetime import datetime
import copy

import numpy as np
import xarray as xr
import pyinterp.backends.xarray
import pyinterp.fill

import alan_tools.config as cfg
import alan_tools.file_attributes as attrs


def fill_and_regrid(in_arr, mx, my):
    '''
    Use pyinterp module to fill in some of the NaNs at the coast and to
    interpolate data to target grid.

    Args:

    in_arr (xarray.DataArray): Input array to move to target grid.
    mx (numpy.array): Array of target longitudes.
    my (numpy.array): Array of target latitudes.

    Returns:

    regridded.T: numpy.array containing regridded input.

    '''
    grid = pyinterp.backends.xarray.Grid2D(in_arr)
    filled = pyinterp.fill.loess(grid, nx=3, ny=3)
    # pyinterp.fill returns a numpy array so put back in DataArray.
    # Also need to transpose data.
    filled_ds = in_arr.copy()
    filled_ds.data = filled.T

    interpolator = pyinterp.backends.xarray.Grid2D(filled_ds)
    regridded = interpolator.bivariate(
        coords=dict(lon=mx.ravel(), lat=my.ravel())).reshape(mx.shape)

    return regridded.T


class ALANTile:
    '''
    Class for creating objects containing data used for calculating ALAN
    tiles, with methods for calculating, saving and plotting the critical
    depth (z_thresh) output.

    '''

    def __init__(
            self, region_name, roi, month, kd_dir=cfg.KD_DIR,
            kd_fpattern=cfg.KD_FPATTERN, falchi_path=cfg.FALCHI_PATH,
            landmask_path=cfg.LANDMASK_PATH):
        '''
        Args:

        region_name (str): Name for the region of interest
        roi (tuple): Coordinates for the region of interest (S, N, W, E).
        month (str): Month used for Kd input.
        kd_dir (str): Optionally override directory containing Kd files.
        kd_fpattern (str): Optionally override file pattern for Kd files.
        falchi_path (str): Optionally override full path to Falchi data.
        landmask_path (str): Optionally override full path to landmask file.

        '''
        self.region_name = region_name
        self.roi = roi
        self.min_lat, self.max_lat, self.min_lon, self.max_lon = self.roi
        self.month = month

        self.kd_path = Path(kd_dir) / kd_fpattern.format(month=month)
        self.falchi_path = falchi_path
        self.landmask_path = landmask_path

        # Read in and transform the input data.
        self.landmask_data = self.get_landmask_data()
        self.target_grid = self.landmask_data
        self.lat, self.lon = self.target_grid.lat, self.target_grid.lon

        self.falchi_data = self.get_falchi_data()
        self.falchi_regridded = self.regrid_falchi()
        self.falchi_masked = self.mask_falchi()

        self.kd_data = self.get_kd_data()
        self.kd_regridded = self.regrid_kd()

        # Calculate critical depth (z_thresh).
        self.z_thresh = self.calculate_z_thresh()

    def get_landmask_data(self):
        '''Read in the landmask and extract ROI.'''
        landmask = xr.open_zarr(self.landmask_path)
        landmask_roi = landmask.sel(
            lat=slice(self.max_lat, self.min_lat),
            lon=slice(self.min_lon, self.max_lon))
        return landmask_roi

    def get_falchi_data(self):
        '''
        Read in the Falchi data and extract ROI. Add coord attributes required
        by pyinterp methods.

        '''
        falchi = xr.open_rasterio(self.falchi_path)
        # Read in the Falchi data with 1deg buffer to avoid issues
        # interpolating to values outside range of Falchi data.
        falchi_roi = falchi.sel(
            y=slice(self.max_lat + 1, self.min_lat - 1),
            x=slice(self.min_lon - 1, self.max_lon + 1))

        falchi_roi = falchi_roi.rename({'x': 'lon', 'y': 'lat'})
        falchi_roi.lat.attrs = attrs.LAT_META
        falchi_roi.lon.attrs = attrs.LON_META
        return falchi_roi

    def regrid_falchi(self):
        '''
        Put the Falchi data onto target grid.
        Note that the data should already be on the same grid, but there are
        some rounding errors in lats/lons so doing for consistency in coords.

        '''
        mx, my = np.meshgrid(
            self.lon.data, self.lat.data, indexing='ij')
        regridded = fill_and_regrid(self.falchi_data[0], mx, my)
        return regridded

    def mask_falchi(self):
        '''Apply mask for low Falchi data values.'''
        falchi_masked = np.where(
            self.falchi_regridded <= cfg.FALCHI_MASK_THRESHOLD,
            np.nan, self.falchi_regridded)
        return falchi_masked

    def get_kd_data(self):
        '''
        Read in the Kd data and extract ROI. Replace fill value with NaNs.

        '''
        kd_data = xr.open_dataset(self.kd_path)
        # Read in the Kd data with 1deg buffer to avoid issues interpolating
        # to values outside range of Kd data.
        kd_roi = kd_data.sel(
            lat=slice(self.max_lat + 1, self.min_lat - 1),
            lon=slice(self.min_lon - 1, self.max_lon + 1))

        kd_roi = kd_roi.where(kd_roi != cfg.KD_FILLVAL)
        return kd_roi

    def regrid_kd(self):
        '''Put the Kd data onto target grid. Returns Dict of numpy arrays.'''
        kd_regridded = {}
        mx, my = np.meshgrid(
            self.lon.data, self.lat.data, indexing='ij')
        for channel in ['kd_blue', 'kd_red', 'kd_green']:
            regridded = fill_and_regrid(self.kd_data[channel][0], mx, my)
            kd_regridded[channel] = regridded
        return kd_regridded

    def apply_landmask(self, in_arr):
        '''
        Apply the landmask to the input array and return masked array.
        The dimensions of input need to match landmask data.

        Args:

        in_arr (numpy.array): Array to be masked.

        '''
        land_mask = ~(self.landmask_data.landmask.compute() == 255).data
        masked_arr = in_arr.copy()
        masked_arr[land_mask] = np.nan
        return masked_arr

    def calculate_z_thresh(self):
        '''
        Calculate the critical depth using Falchi and Kd inputs.
        Apply landmask to result.

        '''
        # Calculate the above water values of irradiance in the blue, green,
        # red. Falchi units are in mCd/m2. Irradiance is in uW/m2.
        # Calculation with offset added (7/3/21). This corroborated by
        # working with the Tamir data in Eilat.
        sfce_irr_blue_uW_m2 = cfg.M_BLUE * self.falchi_masked + cfg.C_BLUE
        sfce_irr_green_uW_m2 = cfg.M_GREEN * self.falchi_masked + cfg.C_GREEN
        sfce_irr_red_uW_m2 = cfg.M_RED * self.falchi_masked + cfg.C_RED
        sfce_irr_total_uW_m2 = \
            sfce_irr_blue_uW_m2 + sfce_irr_green_uW_m2 + sfce_irr_red_uW_m2

        R_blue = sfce_irr_blue_uW_m2 / sfce_irr_total_uW_m2
        R_green = sfce_irr_green_uW_m2 / sfce_irr_total_uW_m2
        R_red = sfce_irr_red_uW_m2 / sfce_irr_total_uW_m2

        Kd_log_expression = \
            R_blue.data * np.exp(-1.0 * self.kd_regridded['kd_blue']) + \
            R_green.data * np.exp(-1.0 * self.kd_regridded['kd_green']) + \
            R_red.data * np.exp(-1.0 * self.kd_regridded['kd_red'])

        Kd_total = np.where(
            np.logical_and(Kd_log_expression > 0.,
                           ~np.isnan(Kd_log_expression)),
            -1.0 * np.log(Kd_log_expression),
            np.nan
        )
        Kd_total = np.where(Kd_total > 0.0, Kd_total, np.nan)

        z_thresh = (-1.0 / Kd_total) * np.log(
            cfg.THRESH_IRR_TOTAL_UW_M2 / sfce_irr_total_uW_m2)

        z_thresh = self.apply_landmask(z_thresh)
        return z_thresh

    def make_z_thresh_dataset(self):
        '''
        Put the z_thresh numpy array in an xarray dataset.
        Add attributes to the variables.

        '''
        # Force all time values to be 2019-{Month}-01
        self.days_difference_since_19700101 = [(
            datetime(cfg.YEAR_VALUE_TO_COERCE_DATES, int(self.month), 1)
            - datetime(1970, 1, 1)).days]

        # Edit the global attributes here
        edited_attrs = copy.deepcopy(attrs.global_attributes)
        edited_attrs['title'] = edited_attrs['title'].replace(
            'REGION_PLACEHOLDER', self.region_name)
        edited_attrs['extents'] = edited_attrs['extents'].replace(
            'SPATIAL_PLACEHOLDER',
            f'Latitude: [{self.min_lat},{self.max_lat}] '
            f'Longitude: [{self.min_lon},{self.max_lon}]')
        edited_attrs['abstract'] = edited_attrs['abstract'].replace(
            'SPATIAL_PLACEHOLDER',
            f'Latitude: [{self.min_lat},{self.max_lat}] '
            f'Longitude: [{self.min_lon},{self.max_lon}]')
        edited_attrs['creation_date'] = edited_attrs['creation_date'].replace(
            'CREATION_PLACEHOLDER', f'{datetime.now().strftime("%d/%m/%Y")}')

        z_thresh_ds = xr.Dataset(
            data_vars={
                'z_thresh': (
                    ['time', 'lat', 'lon'],
                    np.expand_dims(self.z_thresh, axis=0),
                    # Set the z_thresh attributes here.
                    attrs.z_thresh_attributes
                )
            },
            coords={
                'time': (
                    ['time'],
                    self.days_difference_since_19700101,
                    attrs.TIME_META),
                'lat': (['lat'], self.lat.data, attrs.LAT_META),
                'lon': (['lon'], self.lon.data, attrs.LON_META),
            },
            # Set the global attributes here
            attrs=edited_attrs,
        )
        # Replace NaNs with a value
        z_thresh_ds['z_thresh'].data = z_thresh_ds['z_thresh'].fillna(
            cfg.VALUE_TO_REPLACE_NANS)

        # Add additional lat attributes here.
        z_thresh_ds['lat'].attrs['valid_min'] = -90.0
        z_thresh_ds['lat'].attrs['valid_max'] = 90.0

        # Add additional lon attributes here.
        z_thresh_ds['lon'].attrs['valid_min'] = -180.0
        z_thresh_ds['lon'].attrs['valid_max'] = 180.0

        return z_thresh_ds

    def make_output_fname(self, region_name=None):
        '''
        Create string for the output filename.

        Args:

        region_name (str): Optionally add a region name to end of fname.

        '''
        if region_name:
            region_str = f'_{region_name}'
        else:
            region_str = ''
        return f'In-water_clear-sky_ALAN_Zc_Month-{self.month}_' \
               f'{self.min_lat}S_{self.max_lat}N_' \
               f'{self.min_lon}W_{self.max_lon}E{region_str}.nc'

    def save_z_thresh_to_nc(
            self, output_dir='./', output_fname=None, region_name=None):
        '''
        Save the critical depth output to a netcdf file.

        Args:

        output_dir (str):
            Optionally provide path to output dir (default current dir).
        output_fname (str): Optionally override the default filename.
        region_name (str):
            If using default filename can optionally add the region name to
            end of filename.

        '''
        fname = output_fname or self.make_output_fname(region_name)
        z_thresh_ds = self.make_z_thresh_dataset()
        output_path = Path(output_dir) / fname
        encoding = {
            'z_thresh': {'zlib': True, 'complevel': 5},
            'lat': {'_FillValue': None},
            'lon': {'_FillValue': None}
        }
        z_thresh_ds.to_netcdf(output_path, encoding=encoding)
        return z_thresh_ds

    def display_z_thresh(self):
        '''Display the critical depth data on map.'''
        # Can update with more advanced plot (TO DO).
        z_thresh_ds = self.make_z_thresh_dataset()
        z_thresh_ds.z_thresh.plot(vmin=0, vmax=50)
