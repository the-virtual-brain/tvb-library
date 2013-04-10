def setup_test_console_env():
    import sys
    # Remove anything pointing to the framework, to make sure that only one direct dependency exists
    # TVB-Framework --> TVB Scientific Library
    # We should have nothing inverse.
    sys.path = [path for path in sys.path if not path.endswith('framework_tvb')]
    
    from tvb.basic.profile import TvbProfile as tvb_profile
    # Set the current environment to the test setup
    tvb_profile.set_profile(["-profile", "LIBRARY_PROFILE"])
    
    