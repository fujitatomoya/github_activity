# Github Activity Tools

## Overview

tools and scripts to search the github commit activity based on conditions such as the stars, PRs and so on.

- [check_activity.py](./check_activity.py)
  - using `Github API` to access github.com to collect information based on seeds.
  - see output example [github_activity.graphml](./github_activity.graphml)
- [contribution_report](./contribution_report.py)
  - generate contribution report based on date, user, and organization.

### [check_activity.py](./check_activity.py)

#### Requirement

- Python version 2
- PyGithub v1.25.0
- NetworkX v1.8.1
- Cytoscape 3.1.1

```
$ pip install PyGithub networkx pygraphml
```

#### Usage

1. insert github token as yours in check_activity.py.
2. modify SEEDs as you like in check_activity.py.
3. execute "python check_activity.py"
4. you can use Cytoscape to see the whole mapping.

### [contribution_report.py](./contribution_report.py)

#### Requirement

- Python version 3

#### Usage

```
>python3 contribution_report.py -t <YOUR_GITHUB_TOKEN> -a <ACCOUNTS> -o <ORGANIZATION>
# Contributions
By Authors: fujitatomoya, Barry-Xu-2018, iuhilnehc-ynos
To Repositories in Organizations: ros2
Merged Since: 2020-12-21
This report generated: 2021-01-20
Contribution count (remember to update if you remove things): 6
* ros2/rcl
  * "Improve trigger test for graph guard condition" | Barry Xu | https://github.com/ros2/rcl/pull/811 (merged 2020-12-22)
  * "Re-add "Improve trigger test for graph guard condition (#811)"" | Barry Xu | https://github.com/ros2/rcl/pull/884 (merged 2021-01-11)
* ros2/rclcpp
  * "use describe_parameters of parameter client for test" | tomoya | https://github.com/ros2/rclcpp/pull/1499 (merged 2021-01-12)
  * "add timeout to SyncParametersClient methods" | tomoya | https://github.com/ros2/rclcpp/pull/1493 (merged 2020-12-22)
* ros2/rosbag2
  * "Fixed playing if unknown message types exist" | Chen Lihui | https://github.com/ros2/rosbag2/pull/592 (merged 2020-12-29)
* ros2/system_tests
  * "update parameter client test with timeout." | tomoya | https://github.com/ros2/system_tests/pull/457 (merged 2020-12-22)
```

## Author

- [TomoyaFujita](https://github.com/tomoyafujita)

## Reference

- https://qiita.com/keiono/items/aacffd0e9ae65e2b51b0
