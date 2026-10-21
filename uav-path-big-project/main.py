from environment.environment import UAVEnvironment


def main():
    uav_map = UAVEnvironment(100, 100)
    uav_map.visualize()


if __name__ == "__main__":
    main()
