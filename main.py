import saltpaper as salt

def init():
    ins = salt.InputService()
    ds = salt.DisplayService(
        dimensions=(400,300),
        inputservice = ins,
        target_frame_rate=60,
        caption="asset service test"
    )
    print()

    main_layer = salt.Layer(
        dimensions=ds.dimensions
    )
    ds.add_layer(main_layer)
    world = salt.World()
    ass = salt.AssetService()
    rs = salt.RenderService(world, ass)

    test_entity = salt.make_test_entity(world, main_layer, 100,100)

    while ds.running:
        ds.tick()
        rs.tick()

if __name__ == "__main__":
    init()