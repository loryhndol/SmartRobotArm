import sys, os

sys.path.extend([
    os.path.join(root, name) for root, dirs, _ in os.walk("../")
    for name in dirs
])

from utility.point3d import Point3d
import workspace as ws
import matplotlib.pyplot as plt
import numpy as np


def plot_scene(ax, bags, partition):
    plt.cla()
    num_of_bags = len(bags)
    # Create axis
    axes = [partition[0], partition[1], partition[2]]

    # Create Data
    data = np.ones(axes)
    for k in range(partition[2]):
        for j in range(partition[1]):
            for i in range(partition[0]):
                warp_size = partition[0] * partition[1]
                idx = warp_size * k + partition[0] * j + i
                if idx >= num_of_bags:
                    data[i][j][k] = 0
                elif bags[idx].empty:
                    data[i][j][k] = 0

    # Voxels is used to customizations of
    # the sizes, positions and colors.
    ax.voxels(data, edgecolors='grey')
    plt.pause(.5)


# Plot figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
target = 800
eps = 50
cur_weight = 0
res: list[ws.Bag] = []
finished = False
partition = (2, 2, 3)
num_of_bags = 12
test_workspace = ws.Workspace(position=Point3d(0.0, 0.0, 0.0),
                              x_range=100,
                              y_range=100,
                              z_range=100,
                              partition=partition)

try:
    test_workspace.generate_bags(num_of_bags)

    for bag in test_workspace.bags:
        idx = bag.ID
        print("ID: {} Position: {} Weight: {}".format(idx, bag.center,
                                                      bag.weight))

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
            if not finished:
                while test_workspace.peek(row, col):
                    plot_scene(ax, test_workspace.bags,
                               test_workspace.partition)
                    obj_info = test_workspace.top(row, col)
                    lookahead = cur_weight + obj_info.weight
                    if lookahead < target + eps:
                        cur_weight += obj_info.weight
                        res.append(obj_info)
                        if lookahead > target - eps:
                            finished = True
                            break
                    else:
                        break

    if finished:
        print("Success! cur: {} target: {} eps: {}".format(
            cur_weight, target, eps))
        for i in res:
            print(i.weight)

    elif cur_weight < target - eps or cur_weight > target + eps:
        print("Failed: cur: {} target: {} eps: {}".format(
            cur_weight, target, eps))

except Exception as err:
    print(err)
