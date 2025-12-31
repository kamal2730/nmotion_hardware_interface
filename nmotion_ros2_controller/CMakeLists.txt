cmake_minimum_required(VERSION 3.8)
project(nmotion_ros2_controller)

# Compiler warnings
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Required for nmotion SDK
add_compile_options(-D_GLIBCXX_USE_CXX11_ABI=1)

# =====================
# Dependencies
# =====================
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)

# =====================
# Hardware plugin
# =====================
add_library(nmotion_ros2_controller SHARED
  src/nmotion_system.cpp
)

# Include directories
target_include_directories(nmotion_ros2_controller PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/nmotion_transport/include>
  $<INSTALL_INTERFACE:include>
)

# =====================
# NMotion SDK (imported)
# =====================
add_library(nmotion_transport SHARED IMPORTED)
set_target_properties(nmotion_transport PROPERTIES
  IMPORTED_LOCATION
    ${CMAKE_CURRENT_SOURCE_DIR}/nmotion_transport/lib/libnmotion_transport.so
)

target_link_libraries(nmotion_ros2_controller
  nmotion_transport
)

ament_target_dependencies(nmotion_ros2_controller
  rclcpp
  hardware_interface
  pluginlib
  rclcpp_lifecycle
)

# =====================
# Plugin export
# =====================
pluginlib_export_plugin_description_file(
  hardware_interface
  plugin.xml
)

# =====================
# Install
# =====================
install(
  TARGETS nmotion_ros2_controller
  LIBRARY DESTINATION lib
)

install(
  DIRECTORY include/
  DESTINATION include
)
install(
  FILES nmotion_transport/lib/libnmotion_transport.so
  DESTINATION lib
)

# =====================
# Testing (unchanged)
# =====================
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
