#include "nmotion_ros2_controller/nmotion_system.hpp"

#include <cmath>
#include <pluginlib/class_list_macros.hpp>
#include <rclcpp/rclcpp.hpp>

#include <nmotion_transport/usb_interface.hpp>

namespace nmotion_ros2_controller
{

hardware_interface::CallbackReturn
NMotionSystem::on_init(const hardware_interface::HardwareInfo & info)
{
  if (SystemInterface::on_init(info) != CallbackReturn::SUCCESS) {
    return CallbackReturn::ERROR;
  }

  if (info.hardware_parameters.count("device")) {
    device_ = info.hardware_parameters.at("device");
  }

  if (info.hardware_parameters.count("node_id")) {
    node_id_ = std::stoi(info.hardware_parameters.at("node_id"));
  }

  iface_ = new USBInterface();
  iface_->initInterface(device_);

  actuator_ = new Actuator(node_id_, iface_);

  return CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn
NMotionSystem::on_activate(const rclcpp_lifecycle::State &)
{
  actuator_->clearActuatorErrors();
  actuator_->setDeviceToActive();
  return CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn
NMotionSystem::on_deactivate(const rclcpp_lifecycle::State &)
{
  if (actuator_) {
    actuator_->setDeviceToIdle();
  }

  if (iface_) {
    iface_->closeInterface();
  }

  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
NMotionSystem::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> interfaces;
  interfaces.emplace_back("joint1", "position", &pos_);
  interfaces.emplace_back("joint1", "velocity", &vel_);
  interfaces.emplace_back("joint1", "effort", &eff_);
  return interfaces;
}

std::vector<hardware_interface::CommandInterface>
NMotionSystem::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> interfaces;
  interfaces.emplace_back("joint1", "position", &cmd_pos_);
  interfaces.emplace_back("joint1", "velocity", &cmd_vel_);
  interfaces.emplace_back("joint1", "effort", &cmd_eff_);
  return interfaces;
}

hardware_interface::return_type
NMotionSystem::read(const rclcpp::Time &, const rclcpp::Duration &)
{
  float pos_deg = 0.0f;
  float vel_deg = 0.0f;
  float torque_nm = 0.0f;

  actuator_->getOutputPosition(&pos_deg);
  actuator_->getOutputVelocity(&vel_deg);
  actuator_->getOutputTorque(&torque_nm);

  pos_ = pos_deg * M_PI / 180.0;
  vel_ = vel_deg * M_PI / 180.0;
  eff_ = torque_nm;

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type
NMotionSystem::write(const rclcpp::Time &, const rclcpp::Duration &)
{
  
  actuator_->setPositionControl(
    static_cast<float>(cmd_pos_ * 180.0 / M_PI),
    90.0f
  );

  return hardware_interface::return_type::OK;
}

}  // namespace nmotion_ros2_controller

PLUGINLIB_EXPORT_CLASS(
  nmotion_ros2_controller::NMotionSystem,
  hardware_interface::SystemInterface)
