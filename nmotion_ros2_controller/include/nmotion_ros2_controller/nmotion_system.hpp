#pragma once

#include <hardware_interface/system_interface.hpp>
#include <hardware_interface/types/hardware_interface_return_values.hpp>
#include <rclcpp_lifecycle/state.hpp>
#include <rclcpp/macros.hpp>

#include "nmotion_transport/actuator.hpp"
#include "nmotion_transport/interface.hpp"
#include "nmotion_transport/usb_interface.hpp"



namespace nmotion_ros2_controller
{

class NMotionSystem : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(NMotionSystem)

  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  std::vector<hardware_interface::StateInterface>
  export_state_interfaces() override;

  std::vector<hardware_interface::CommandInterface>
  export_command_interfaces() override;

  hardware_interface::return_type read(
    const rclcpp::Time & time,
    const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time,
    const rclcpp::Duration & period) override;

private:
  Interface *iface_{nullptr};
  Actuator *actuator_{nullptr};

  double pos_{0.0};
  double vel_{0.0};
  double eff_{0.0};

  double cmd_pos_{0.0};
  double cmd_vel_{0.0};
  double cmd_eff_{0.0};

  uint32_t node_id_{0};
  std::string device_{"/dev/ttyACM0"};
};

}  // namespace nmotion_ros2_controller
