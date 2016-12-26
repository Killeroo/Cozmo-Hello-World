#!/usr/bin/env python3

import asyncio
import time

import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps


def cozmo_hello_world_program(robot: cozmo.robot.Robot):
    # display some cosmo verbose
    cozmo.logger.info("--------------------------")
    cozmo.logger.info("cozmo_hello_world_program started.")
    cozmo.logger.info("battery at " + str(robot.battery_voltage) + "volts")
    cozmo.logger.info("accelerometer " + str(robot.accelerometer))

    # locate objects in world
    find_objects(robot)

    # move forward then turn in a circle
    robot.drive_straight(distance_mm(100), speed_mmps(75)).wait_for_completed()
    robot.turn_in_place(degrees(180)).wait_for_completed()
    robot.turn_in_place(degrees(180)).wait_for_completed()

    # nod his head
    robot.set_head_angle(cozmo.robot.MIN_HEAD_ANGLE).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    robot.set_head_angle(cozmo.robot.MIN_HEAD_ANGLE).wait_for_completed()

    # wait a second
    time.sleep(1)

    # say some stuff
    robot.say_text("hai", True).wait_for_completed()

    cozmo.logger.info("--------------------------")


def find_objects(robot: cozmo.robot.Robot):
    # locate objects in world
    charger = None

    # look for charger #
    # see if cozmo knows where charger is
    if robot.world.charger:
        if robot.world.charger.pose.is_comparable(robot.pose):
            # cozmo knows the position of the charger relative to him
            charger = robot.world.charger
        else:
            # cozmo knows the charger is in the world but doesn't know exactly where
            # probably been moved, search for charger
            pass

    # if charger hasn't been found search for it
    if not charger:
        cozmo.logger.info("Searching for charger...")
        # create an action/behaviour for cozmo to look around
        look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try:
            # can cozmo see the charger after 30 seconds
            charger = robot.world.wait_for_observed_charger(timeout=30)
            charger = charger.pose.position
            cozmo.logger.info("charger found.")
            look_around.stop()
            robot.say_text("found it", True).wait_for_completed()
        except asyncio.TimeoutError:
            cozmo.logger.warn("charger not found.")
            charger = "UNKNOWN"
        finally:
            # stop looking
            look_around.stop()

    cozmo.logger.info("Charger location: " + str(charger))

    # look for light cubes #
    # tell cozmo to start looking around
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

    # tell cozmo to look for three light cube objects
    cubes = robot.world.wait_until_observe_num_objects(num=3, object_type=cozmo.objects.LightCube, timeout=60)

    # stop looking once 3 are found
    look_around.stop()

    cozmo.logger.info("Found " + str(len(cubes)) + " Cube(s):")
    if len(cubes) > 0:
        for cube in cubes:
            cozmo.logger.info(str(cube.pose.position))

    # flash found light cubes
    if len(cubes) > 0:
        i = 0
        while i < 10:
            for cube in cubes:
                cube.set_light_corners(cozmo.lights.green_light, cozmo.lights.red_light, cozmo.lights.green_light,
                                       cozmo.lights.red_light)

            time.sleep(0.5)

            for cube in cubes:
                cube.set_light_corners(cozmo.lights.red_light, cozmo.lights.green_light, cozmo.lights.red_light,
                                       cozmo.lights.green_light)

            time.sleep(0.5)

            i += 1


# entry point
cozmo.run_program(cozmo_hello_world_program)
