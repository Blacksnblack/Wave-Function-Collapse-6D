from Collapser import *
from Visualizer import Visualizer as vis
# from Visualizer_New import Visualizer as vis
from random import randint as rand
import json

filename_6D = "data.json"
filename_3D = "data_3d.json"


def get_rotation_indexes():  # calculated these out but don't need it to calculate every time it's ran
    return {
        'right': [2, 11, 20, 5, 14, 23, 8, 17, 26, 1, 10, 19, 4, 13, 22, 7, 16, 25, 0, 9, 18, 3, 12, 21, 6, 15, 24],
        'left': [18, 9, 0, 21, 12, 3, 24, 15, 6, 19, 10, 1, 22, 13, 4, 25, 16, 7, 20, 11, 2, 23, 14, 5, 26, 17, 8],
        'back': [20, 19, 18, 23, 22, 21, 26, 25, 24, 11, 10, 9, 14, 13, 12, 17, 16, 15, 2, 1, 0, 5, 4, 3, 8, 7, 6]
    }


def rotate_piece(name: str, data: str, rot_key: dict):
    pieces = {name + "_forward": data}
    for direction, rot_data in rot_key.items():
        new_name = f"{name}_{direction}"
        new_data = ""
        for rd in rot_data:
            new_data += data[rd]
        pieces[new_name] = new_data
    return pieces


def get_basic_3D_shapes():
    pieces_str = {
        "flat_top": "111000000" * 3,
        "flat_middle": "000111000" * 3,
        "flat_bottom": "000000111" * 3,
    }
    rotatable_pieces = {
        "stairs": "000000111000111000111000000",
        "stairs_corner_fl": "000000111000110001100010001",
        "half_stairs_1": "000000111000111000000111000",
        "half_stairs_2": "000000111000000111000111000",
        "half_stairs_1_corner": "000000111000110001000110001",
        "half_stairs_2_corner": "000000111000000111000100011",
        "half_stairs_12_corner": "000000111000100011000100011",
        "half_stairs_21_corner": "000000111000000111000110001",
    }

    rot_key = get_rotation_indexes()
    for name, p_data in rotatable_pieces.items():
        pieces_str.update(rotate_piece(name, p_data, rot_key))
    # Ideally save all pieces and rotated ones to file instead of creating on the fly
    return pieces_str


def create_simple_3d_pieces():
    # simple 3d shapes
    # random color for each piece
    pieces_str = get_basic_3D_shapes()
    print(f"Created {len(pieces_str)} 3D pieces.")
    Pieces = []

    for name, piece in pieces_str.items():
        # print(name, piece)
        color = (
            rand(0, 255) / 255,
            rand(0, 255) / 255,
            rand(0, 255) / 255, 1.0)
        Pieces.append(Piece3D(name, piece, color=color))
    return Pieces


def create_and_save_6d_objs(size: int, filename: str):
    """
    Attempts to create 6D shapes from using 27 grids each
    containing sizexsize 3x3x3 sections and saves them
    to filename.
    Shapes usually end up NOT being very compatible with each-other though.
    :param size: size of the grid
    :param filename: name of file to save 6D Shapes
    :return: N/A
    """
    collapser = Controller(
        pieces=create_simple_3d_pieces(),
        rows=size,
        cols=size
    )
    objs_6D = [[] for x in range(size * size)]
    for i in range(27):  # 3x3x3; dimensions 4,5,6
        grid = [ele for row in collapser.redo_grid() for ele in row]
        for j, ele in enumerate(grid):
            objs_6D[j].append(ele)
    objs_6D = [Piece6D(x) for x in objs_6D]
    # remove duplicates
    objs_6D_hashes = [x.hash for x in objs_6D]
    counter = 0
    print(len(objs_6D))
    for i in range(len(objs_6D) - 1, -1, -1):
        if objs_6D_hashes.count(objs_6D[i].hash) > 1:
            objs_6D.pop(i)
            counter += 1
    print(f"removed {counter} duplicate 6D objects.")

    collapser.reset()

    with open(filename, "w") as f:
        json.dump(objs_6D, f, sort_keys=False)
    print(f"created and saved {len(objs_6D)} 6D objs")


def load_6d_objs(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    objs_6d = []
    counter = 0
    colors = [(rand(0, 255) / 255, rand(0, 255) / 255, rand(0, 255) / 255, 1) for x in range(27)]
    for d in data:
        objs_3d = []
        # color_ind = rand(0, 100) % 3
        for i, ele in enumerate(d["data_6D"]):
            # Offset color a bit ---
            color_list = list(colors[i])
            x = 20
            color_list[0] += (rand(-x, x) / 255)
            color_list[1] += (rand(-x, x) / 255)
            color_list[2] += (rand(-x, x) / 255)

            color_list[0] = max(min(color_list[0], 1.0), 0.0)
            color_list[1] = max(min(color_list[1], 1.0), 0.0)
            color_list[2] = max(min(color_list[2], 1.0), 0.0)
            # -------------------------
            objs_3d.append(Piece3D(str(i), ele["data_3D"], tuple(color_list)))
        objs_6d.append(Piece6D(objs_3d))
        counter += 1
    print(f"Loaded {counter} 6D objects from '{filename}'")
    return objs_6d


def load_3d_pieces():
    with open(filename_3D, "r") as f:
        data = json.load(f)
    pieces = []
    for shape in data:
        pieces.append(Piece3D(name=shape["name"], data=shape["data_3D"], color=tuple(shape["color"])))
        print(pieces[-1].color)
    return pieces


def create_save_3d_pieces():
    with open(filename_3D, "w") as f:
        data = create_simple_3d_pieces()
        json.dump(data, f, sort_keys=False)


def main():
    # create_save_6d_objs(100, filename=filename)
    # exit()

    size = 15
    Collapse_Controller = Controller(
        # pieces = load_3d_pieces()  # can switch to this to just run 3D (Visualizer won't do 6D stuff)
        pieces=load_6d_objs(filename_6D),
        rows=size,
        cols=size
    )

    v = vis(Collapse_Controller)
    v.run()


if __name__ == "__main__":
    main()
    # test()
