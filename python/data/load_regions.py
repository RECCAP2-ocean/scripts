
def get_reccap2ocean_regions(
    url='https://github.com/RECCAP2-ocean/R2-shared-resources/raw/master/data/regions/RECCAP2_region_masks_all_v20210412.nc',
    dest='../data/regions/',
):
    """
    Downloads the latetst RECCAP2 ocean masks and returns as an xarray.Dataset
    """
    from . download import download
    from xarray import open_dataset
    
    fname = download(url, path=dest)
    ds = open_dataset(fname)
    
    return ds


def get_southern_ocean_subregions():
    """
    Gets the Southern Ocean masks for the RECCAP2 Southern Ocean chapter

    Can be broken down into biomes and basins. Biomes are from Fay and 
    McKinley (2014). 
    Basins boundaries are:
        Cape Town, South Africa: ~20°E, 
        Hobart, Tasmania: ~147°E, 
        Cape Horn, South America: ~290°E
    
    The intersection of this three by three grid produces nine subregions
    """
    import xarray as xr
    import pandas as pd
    import itertools
    
    ds = get_reccap2ocean_regions()

    mask = ds.southern
    
    atlantic = (((mask.lon > 290) | (mask.lon <=  20)) & (mask > 0)).astype(int) * 1
    indian   = (((mask.lon >  20) & (mask.lon <= 147)) & (mask > 0)).astype(int) * 2
    pacific  = (((mask.lon > 147) & (mask.lon <= 290)) & (mask > 0)).astype(int) * 3

    mask = xr.Dataset()
    mask['biomes'] = ds.southern.copy()
    mask['basins'] = (pacific + atlantic + indian).transpose('lat', 'lon')
    
    mask['subregions'] = (mask.basins * 3 + mask.biomes - 3).where(lambda a: a>0).fillna(0).astype(int)
    
    basin = ['ATL', 'IND', 'PAC']
    biome = ['STSS', 'SPSS', 'ICE']
    names = ['-'.join(l) for l in itertools.product(basin, biome)]    
    mask['names'] = xr.DataArray(names, coords={'idx': range(1, 10)}, dims=('idx'))
    mask['names'].attrs['description'] = 'Names for the subregions'
    
    mask['subregions'].attrs['description'] = '(basins * 3 + biomes - 3)'
    mask['basins'].attrs['description'] = 'Atlantic = 1, Indian = 2, Pacific = 3'
    mask['biomes'].attrs['description'] = 'Biomes based on Fay and McKinley (2014), STSS=1, SPSS=2, ICE=3'
    mask.attrs['date'] = pd.Timestamp.today().strftime('%Y-%m-%d')
    return mask
