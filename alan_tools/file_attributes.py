'''Metadata File for ALAN data.'''

global_attributes = {
    'title': 'REGION_PLACEHOLDER Region of Artifical Light at Night Under the Sea',
    'purpose_and_summary': 'Why: To map the extent of artificial light pollution in the marine environment.  What: the depth to which biologically relevant light levels of artificial light pollution penetrate within the water column. Algorithm described in Smyth et al., (2021) (doi.org/10.1525/elementa.2021.00049)',
    'keywords': 'Artificial Light at Night, Pollution, Ecological Response, Ecological Stressors, Ocean Optics, Bio-optics, Remote Sensing',
    'abstract': "Coastlines globally are increasingly being illuminated with Artificial Light At Night (ALAN) from various urban infrastructures such as houses, offices, piers, roads, ports and dockyards. Artificial sky glow can now be detected above 22% of the world's coasts nightly and will dramatically increase as coastal human populations more than double by the year 2060. One of the clearest demonstrations that we have entered another epoch, the urbanocene, is the prevalence of ALAN visible from space. Photobiological life history adaptations to the moon and sun are near ubiquitous in the surface ocean (0-200m), such that cycles and gradients of light intensity and spectra are major structuring factors in marine ecosystems. The potential for ALAN to reshape the ecology of coastal habitats by interfering with natural light cycles and the biological processes they inform is increasingly recognized and is an emergent focus for research. The spatial extent covers: SPATIAL_PLACEHOLDER. The temporal extent covers climatological months January-December representing data between 1997-2019.",
    'credits': "Smyth, Timothy J (PML); Nicola Martin (PML), Benjamin O'Driscoll (PML)",
    'resource_constraints': 'This material is licensed under a Creative Commons - Attribution 4.0 International licence',
    'topic_category': 'Environment, Oceans, Biota, Location, Society',
    'creation_date': 'CREATION_PLACEHOLDER',
    'publication_date': 'DD/MM/YYYY',
    'metadata_contact_name': 'Firstname Lastname',
    'metadata_contact_organisation': 'Organisation name',
    'metadata_contact_phone': 'Contact number',
    'metadata_contact_email': 'Contact email',
    'metadata_contact_address': 'Address line 1',
    'metadata_contact_city': 'City',
    'metadata_contact_state': 'State/County',
    'metadata_contact_postcode': 'Postcode',
    'metadata_maintenace': 'As Needed',
    'resource_status': 'Completed, Ongoing',
    'extents': 'The spatial extent covers: SPATIAL_PLACEHOLDER',
    'resource_contact_name': 'Firstname Lastname',
    'resource_contact_organisation': 'Organisation name',
    'resource_contact_phone': 'Contact number',
    'resource_contact_email': 'Contact email',
    'resource_contact_address': 'Address line 1',
    'resource_contact_city': 'City',
    'resource_contact_state': 'State/County',
    'resource_contact_postcode': 'Postcode',
    'owner_contact_name': 'Firstname Lastname',
    'owner_contact_organisation': 'Organisation name',
    'owner_contact_phone': 'Contact number',
    'owner_contact_email': 'Contact email',
    'owner_contact_address': 'Address line 1',
    'owner_contact_city': 'City',
    'owner_contact_state': 'State/County',
    'owner_contact_postcode': 'Postcode',
    'resource_maintenance': 'As Needed',
    'spatial_reference': 'WGS 84',
    'resolution': '30 arcsec (1km)',
    'resource_lineage_dataset_creation_and_alteration': "This dataset is derived from two primary satellite data sources: an artificial night sky brightness world atlas (Falchi et al., 2016) and an in-water Inherent Optical Property (Lee et al., 2002) dataset derived from ESA's Ocean Colour Climate Change Initiative (OC-CCI https://www.oceancolour.org/). These primary datasets are both used in conjunction with in-situ derived measurements and radiative transfer modelling in order to quantify the critical depth (Zc) to which biologically relevant ALAN penetrates throughout the global ocean's estuarine, coastal and near shore regions, in particular the area defined by an individual country's Exclusive Economic Zone.",
    'resource_lineage_dataset_source': 'Original dataset repository - https://doi.pangaea.de/10.1594/PANGAEA.929749 which should be considered Version 1 release.  Small coding changes for this dataset to include more accurate positional information and improved handling of spectral artifacts.',
    'supplemental_information': 'Filenaming conventions: In-water_clear-sky_ALAN_Zc_Month-MM_aaS_bbN_ccW_ddE_AAA.nc. Where MM is month of the year (01 - January); aa, bb, cc, dd define the regional box of interest where: aa is the minimum latitude, bb is the maximum latitude, cc is the minimum longitude, dd is the maximum longitude and AAA is a free-form descriptor of the geographical region of interest. Derived dataset from the primary data by Lee et al., 2002 publication algorithm using the primary dataset of Sathyendranath et al., 2019 (the CCI dataset): ESACCI-OC-MAPPED-CLIMATOLOGY-1M_MONTHLY_4km_GEO_PML_OCx_QAA-Kd-mm-fv4.0.nc where mm is the month of the year (01 - January).They contain the diffuse attenuation coefficient Kd at three broadband wavelengths, global, at 4 km resolution in geometric projection.',
}

z_thresh_attributes = {
    'long_name':  'Depth below which light threshold reached',
    'units': 'm',
    'alias': 'Critical Depth (m)',
    'level_descr': 'Surface',
    'field_descr': 'The critical depth is defined as the depth at which the modelled light level in the water column, illuminated by ALAN, drops below 0.102 µWm-2, the minimum irradiance of white light that elicits diel vertical migration in adult female Calanus copepods (Batnes et al., 2015). This is function of incident ALAN irradiance at the surface as well as the in-water transparency (governed by in-water optically active constituents).',
    'var_desc': 'Threshold depth: m',
    '_FillValue': -999.0
}

# Metadata for using in DataArrays:
LAT_META = {
    'units': 'degrees_north',
    'long_name': 'latitude',
    'standard_name': 'latitude',
    'axis': 'Y',
}
LON_META = {
    'units': 'degrees_east',
    'long_name': 'longitude',
    'standard_name': 'longitude',
    'axis': 'X',
}
TIME_META = {
    'units': 'days since 1970-01-01 00:00:00',
    'axis': 'T',
    'standard_name': 'time',
    'calendar': 'proleptic_gregorian'
}
