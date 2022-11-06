import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D


def to_screen(point):
    return point[:2]


initial_point = np.array([0.0, 0.0, 0.0])
target_point = np.array([10.0, 52.0, -35.0])
eps = 1e-2

records = initial_point
robot = initial_point
move_dis = np.array([1.0, 1.0, 1.0])

while np.sum(np.abs(to_screen(robot) - to_screen(target_point))) > eps:
    direction = target_point - robot
    for id, value in enumerate(direction):
        if value > 0.0:
            robot[id] += 1.0
        elif value == 0.0:
            continue
        else:
            robot[id] -= 1.0
    records = np.vstack((records, robot))

x = records[:, 0]
y = records[:, 1]
z = records[:, 2]

# 绘制散点图
fig = plt.figure()
ax = Axes3D(fig)
fig.add_axes(ax)
ax.scatter(xs=initial_point[0],
           ys=initial_point[1],
           zs=initial_point[2],
           c='g',
           s=100)
ax.scatter(xs=target_point[0],
           ys=target_point[1],
           zs=target_point[2],
           c='r',
           s=100)
ax.scatter(x, y, z)

# 添加坐标轴(顺序是Z, Y, X)
ax.set_zlabel('Z', fontdict={'size': 15, 'color': 'red'})
ax.set_ylabel('Y', fontdict={'size': 15, 'color': 'red'})
ax.set_xlabel('X', fontdict={'size': 15, 'color': 'red'})

plt.show()