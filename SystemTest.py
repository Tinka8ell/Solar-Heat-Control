"""
Test bed for system specific code
"""
import platform

def main():
    # this is for testing
    print(f"platform:  {platform.platform()}")
    print(f"aliased:   {platform.platform(aliased=True)}")
    print(f"processor: {platform.processor()}")
    print(f"machine:   {platform.machine()}")
    print(f"system:    {platform.system()}")
    return 


# execute only if run as a script
if __name__ == "__main__":
    main()  # execute test code ...
