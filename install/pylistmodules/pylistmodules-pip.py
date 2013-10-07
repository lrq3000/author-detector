import pip

def get_all_package_dependencies():
    """Return dictionary of installed packages to list of package dependencies."""
    return {
        dist.key: [r.key for r in dist.requires()]
        for dist in pip.get_installed_distributions()
    }

print(get_all_package_dependencies())
input("Press Enter to continue...")
