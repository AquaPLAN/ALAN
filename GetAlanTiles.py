#!/usr/bin/env python3
'''Calculate ALAN for regions and months of interest and save to NetCDF.'''
import argparse
import sys
import logging

from alan_tools.alan_tile import ALANTile
import alan_tools.config as cfg

REGION_LOOKUP = {
    'EuropeMed': {
        'name': 'Europe Mediterranean',
        'region': (20, 85, -20, 55)},
    'MidE_NInd': {
        'name': 'Middle East and Northern Indian Ocean',
        'region': (0, 30, 30, 60)},
    'NInd_FarE': {
        'name': 'Northern Indian Ocean, Far East',
        'region': (0, 30, 60, 100)},
    'FarE_Isl': {
        'name': 'Far East and Islands',
        'region': (-10, 30, 100, 130)},
    'Oceania': {
        'name': 'Oceania',
        'region': (-50, 0, 100, 180)},
    'PacRim': {
        'name': 'Pacific Rim',
        'region': (20, 85, 100, 180)},
    'NAm': {
        'name': 'North America',
        'region': (20, 85, -180, -50)},
    'CAm': {
        'name': 'Central America',
        'region': (0, 20, -120, -60)},
    'SAm': {
        'name': 'South America',
        'region': (-60, 0, -90, -30)},
    'NAfr': {
        'name': 'North Africa',
        'region': (0, 30, -20, 20)},
    'SAfr': {
        'name': 'South Africa',
        'region': (-40, 0, 0, 70)},
}
MONTHS_LIST = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
]


parser = argparse.ArgumentParser()
parser.add_argument('output_dir',
                    help='Directory where ALAN outputs will be saved.')
parser.add_argument('--regions', nargs='+', type=str,
                    default=REGION_LOOKUP.keys(),
                    help='List of regions to be processed. Choose from '
                         f'{list(REGION_LOOKUP.keys())}')
parser.add_argument('--months', nargs='+', type=str,
                    default=MONTHS_LIST,
                    help='List of months to be processed. Choose from '
                         f'{MONTHS_LIST}')
parser.add_argument('--kd_dir', default=cfg.KD_DIR,
                    help='Directory containing Kd files.')
parser.add_argument('--kd_fpattern', default=cfg.KD_FPATTERN,
                    help='File pattern for Kd files.')
parser.add_argument('--falchi_path', default=cfg.FALCHI_PATH,
                    help='Full path to Falchi data.')
parser.add_argument('--landmask_path', default=cfg.LANDMASK_PATH,
                    help='Full path to landmask file.')
parser.add_argument('--loglevel', default='DEBUG')
args = parser.parse_args()
logging.basicConfig(level=getattr(logging, args.loglevel.upper()),
                    stream=sys.stdout)

logging.debug(f'Regions to be processed: {args.regions}')
logging.debug(f'Months to be processed: {args.months}')

for region_name in args.regions:
    logging.debug(f'Processing {region_name}')
    roi = REGION_LOOKUP[region_name]['region']
    user_friendly_region_name = REGION_LOOKUP[region_name]['name']
    for month in args.months:
        logging.debug(f'Processing month {month}')
        alan_tile = ALANTile(
            user_friendly_region_name, roi, month, kd_dir=args.kd_dir,
            kd_fpattern=args.kd_fpattern, falchi_path=args.falchi_path,
            landmask_path=args.landmask_path)
        logging.debug(f'Saving results to {args.output_dir}')
        alan_tile.save_z_thresh_to_nc(
            output_dir=args.output_dir, region_name=region_name)
