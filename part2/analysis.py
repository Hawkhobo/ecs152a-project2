

# After running the crawler, we should have a har file containing the hars of the top 1000 sites

# We must then report the number of requests made to third-party domains when visiting each site
# A third party site is a site that does not have the same second-level domain (SLD) as the site you are visiting

# We must identify the top-10 most commonly seen third-parties across all sites
# Can probably achieve this using a map<site, number of times seen>

def analysis(sites, cookies): 



    return sites, cookies    