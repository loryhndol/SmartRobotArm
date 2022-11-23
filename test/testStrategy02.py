import sys, os

sys.path.extend([
    os.path.join(root, name) for root, dirs, _ in os.walk("../")
    for name in dirs
])

from utility.point3d import Point3d
import workspace as ws

target = 300
eps = 10
cur_weight = 0
res = list[ws.Bag]
finished = False
test_workspace = ws.Workspace(position=Point3d(0.0, 0.0, 0.0),
                              x_range=100,
                              y_range=100,
                              z_range=100,
                              partition=(2, 2, 3))

try:
    test_workspace.generate_bags(12)

    for bag in test_workspace.bags:
        idx = bag.ID
        print("ID: {} Position: {}".format(idx, bag.center))

    # 采用深度优先方式对物品进行试探性抓取
    # 到达目的地上方的偏移量
    z_offset_critic = 4
    """
    工作区俯视图示例
    --------------- 
    | 0, 0 | 1, 0 |
    ---------------
    | 0, 1 | 1, 1 |
    ---------------
    """

    for row in range(test_workspace.partition[1]):
        for col in range(test_workspace.partition[0]):
            if finished:
                print("Success!")
                for item in res:
                    print(item.weight)
                exit()

            entry = test_workspace.get_entry(row, col, z_offset_critic)
            print("pos: {}".format(entry))

            while test_workspace.top(row, col) != None:
                obj_info = test_workspace.top(row, col)
                lookahead = cur_weight + obj_info.weight
                if lookahead < target + eps:
                    res.append(obj_info)
                    test_workspace.use(obj_info)
                    if lookahead > target - eps:
                        finished = True
                        break

    if cur_weight < target - eps or cur_weight > target + eps:
        print("Failed: cur: {} target: {} eps: {}".format(
            cur_weight, target, eps))

except Exception as err:
    print(err)
