from gym_city.envs.env import MicropolisEnv

m = MicropolisEnv()
m.setMapSize(20)
m.reset()
go = True
while go:
    m.reset()
    for i in range(500):
        try:
            m.randomStep()
        except KeyError:
            print("KeyError")
            m.printMap()
            m.micro.printTileMap()
            # m.render()  # GUI not supported in Docker
            break
        except AssertionError:
            print("AssertionError")
            m.printMap()
            m.micro.printTileMap()
            # m.render()  # GUI not supported in Docker
            break

        m.printMap()
        # m.micro.printTileMap()
        # m.render()  # GUI not supported in Docker

    go = False  # Set to False to prevent infinite loop

# Gtk.main()  # Remove this since there's no GUI