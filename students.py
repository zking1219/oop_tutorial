#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 15:03:00 2020

@author: zackkingbackup
"""

import math
import abc

import pandas as pd


# The Goal of this program is to simulate the following:
#
# For each person on this list:
# 1. Find the next class they are taking.
# 2. Find the location of that class.
# 3. Find the way to get from your classroom to the person’s next class.
# 4. Tell the person how to get to their next class.


# Define an abstract class, student, with abstract methods that
# will be implemented by the concrete, child classes undergrad_student
# and grad_student
class student(metaclass=abc.ABCMeta):
        
    @abc.abstractmethod
    def get_directions_to_classroom():
        pass
    
   
    def give_instructions(self, instructions, next_location):
        '''
        Function to validate/take action based on the instructions for getting
        to the next class. Update the location if the validation passes.

        Parameters
        ----------
        instructions : string
            Instructions for the student to get to the next class
        next_location : string
            Building and room name

        Returns
        -------
        None.

        '''
        
        # Do anything with the instructions that you wish. You can validate
        # that they do in fact lead to the next_location. You can implement 
        # a student fitness tracker by calculating the number of meters walked
        # and the flights of stairs climbed. 
        student.validate_instructions(instructions)
        print("{} has been told to: {}\nin order to arrive at: {}\n\n".format(self._name, instructions,
                                                                              next_location))
        self._location = next_location
        
    
    def validate_instructions(self, instructions):
        '''
        Do a simple check to ensure the instructions contain the work "Walk".
        This at least guards against the instructions being something like "B2-RM210"
        that could indicate a larger problem in the usage of validate_instructions.
        '''
        assert "Walk" in instructions

        
    def get_location(self):
        '''
        Method to allow read only access to a student's location; protected
        class attributes can't be accessed outside of this class' or this class'
        subclasses' methods.

        Returns
        -------
        string
            Student's location

        '''
        return self._location
    
    
    def get_name(self):
        '''
        Method to allow read only access to a student's name; protected
        class attributes can't be accessed outside of this class' or this class'
        subclasses' methods.

        Returns
        -------
        string
            Student's name

        '''
        return self._name

        
    def get_next_period_location(self):
        '''
        Use schedule and the present location of the student to figure
        out where his or her next class is.

        Returns
        -------
        Location of student's next class as a string
        
        '''
        # What period is is now? Derive it from self.location
        cur_period_idx = self._schedule[self._schedule['ClassLocation'] == self._location].first_valid_index()
        cur_period = self._schedule.at[cur_period_idx, 'Period']
        
        # Return the location of the next class
        return self._schedule[self._schedule['Period'] == cur_period + 1]['ClassLocation'].iat[0]
    
    
    def get_next_classname(self):
        '''
        Use schedule and the present location of the student to figure
        out what his or her next class is.

        Returns
        -------
        Name of student's next class as a string
        
        '''
        # What period is is now? Derive it from self.location
        cur_period_idx = self._schedule[self._schedule['ClassLocation'] == self._location].first_valid_index()
        cur_period = self._schedule.at[cur_period_idx, 'Period']
        
        # Return the name of the next class
        return self._schedule[self._schedule['Period'] == cur_period + 1]['ClassName'].iat[0]
    
    
    def directions_to_room(room):
        '''
        Grad student/Undergrad student agnostic method for getting directions to
        a room number within a building on campus.
        This function is also building agnostic - assume they're laid out the same way.

        Parameters
        ----------
        room : string
            All room names are in B<x>-RM<yyy> format
            where x is the building number and yyy is the room number.

        Returns
        -------
        string
            text directions to the room number from buidling entrance

        '''
        rm_num = room[2:]
        floor = int(rm_num[0])
        num = int(rm_num[1:])
        
        turn_dir = ''
        
        if num % 2 == 0:
            turn_dir = 'right'
        else:
            turn_dir = 'left'
        
        return "Go up {} floor(s), and turn {}".format(floor - 1, turn_dir)
    
    
    def directions_to_building(start, end):
        '''
        Grad student/Undergrad student agnostic method for getting directions to
        a building on campus from another building.
        
        Assume the campus is built around a perfectly circular lake. Each location
        can be defined in terms of polar coordinates, but we'll leave r constant to
        make calculating distances (arclengths) easy.

        Parameters
        ----------
        start : string
            Building student is currently in
        end : string
            Destination building

        Returns
        -------
        string
           text directions to the "end" building from the start 

        '''
        
        theta_start = student.building_locations[start]
        theta_end = student.building_locations[end]
        
        if math.fabs(theta_start - theta_end) > math.pi:
            # need to add 2*pi to the smaller value
            if theta_start < theta_end:
                delta_theta = (2*math.pi + theta_start) - theta_end
                direction = 'clockwise'
            else:
                delta_theta = (2*math.pi + theta_end) - theta_start
                direction = 'counter-clockwise'
        else:
            delta_theta = math.fabs(theta_start - theta_end)
            if theta_start > theta_end:
                direction = 'clockwise'
            else:
                direction = 'counter-clockwise'
            
        # Convert from arclength to distance using the class variable lake_radius
        distance = student.lake_radius*delta_theta
        
        return "Walk {:3.2f} meters {} around the lake".format(distance, direction)


    # Store the theta values in radians for each building in this class attribute
    building_locations = {"B5" : math.pi / 2,
                          "B1" : 0,
                          "B2" : math.pi * 7 / 4,
                          "B3" : math.pi * 5 / 4,
                          "B4" : math.pi * 3 / 4}
    
    # Store the lake's radius for use in calculating distances between buildings
    lake_radius = 150 # meters
    
    # Class variable to contain the conference center room location
    conference_loc = "B4-RM303"
    

# Concrete class for undergraduates
class undergrad_student(student):
    
    # This is the constructor for undergrad_student.
    # The destructor is implictly defined by python.
    def __init__(self, name, current_location, schedule):
        self._name = name
        self._location = current_location
        
        # schedule is a pd.DataFrame with columns "ClassName", "ClassLocation"
        # and "Period"
        self._schedule = schedule
    
    
    # Implement the abstract function from student
    def get_directions_to_classroom(self, class_location):
        '''
        Use the student's current location as well as the location of the next
        class to determine how to walk to class_location.
        
        Returns the instructions as a string.
        '''
        building_start = self._location.split('-')[0]
        building_end = class_location.split('-')[0]
        
        building_directions = student.directions_to_building(building_start, building_end)
        
        destination_room = class_location.split('-')[1]
        
        room_directions = student.directions_to_room(destination_room)
        
        return "{}, then {}.".format(building_directions, room_directions)
    

# Concrete class for graduate students
class grad_student(student):
    
    # This is the constructor for grad_student.
    # The destructor is implictly defined by python.
    def __init__(self, name, current_location, schedule):
        self._name = name
        self._location = current_location
        
        # schedule is a pd.DataFrame with columns "ClassName", "ClassLocation"
        # and "Period"
        self._schedule = schedule
    
    
    # Implement the abstract function from student
    def get_directions_to_classroom(self, class_location):
        '''
        Use the student's current location as well as the location of the next
        class to determine how to walk to class_location.
        
        This function must be modified from the undergrad_student implementation because
        grad students must make a stop at the conference center to drop off
        course evals before they proceed to their next class.
        
        Returns the instructions as a string.
        '''
        
        building_start = self._location.split('-')[0]
        building_end = class_location.split('-')[0]
        destination_room = class_location.split('-')[1]
        
        building_directions_to_conf = student.directions_to_building(building_start,
                                                                     student.conference_loc.split('-')[0])
        
        room_directions_to_conf = student.directions_to_room(student.conference_loc.split('-')[1])
        
        building_directions_to_dest = student.directions_to_building(student.conference_loc.split('-')[0],
                                                                     building_end)
        
        dest_room_directions = student.directions_to_room(destination_room)
        
        return "{}, then {}. Drop off your course evals. Now {}, then {}.".format(
                                    building_directions_to_conf, 
                                    room_directions_to_conf,
                                    building_directions_to_dest,
                                    dest_room_directions)
       

# Helper function to pre-process data into student schedules
def generate_schedule(df, idx):
    '''
    Take the StudentClasses.csv data file and reshape a row of it, indicated by
    idx, into another pandas.DataFrame describing one student's schedule.

    Parameters
    ----------
    df : pandas.DataFrame
        Contents of StudentClasses.csv
    idx : int
        Index of df indicating the row/student whose schedule is to be produced.

    Returns
    -------
    sch_df : pandas.DataFrame
        DataFrame with columns Period, ClassName, and ClassLocation.

    '''
    
    fp = df.at[idx,'First Period']
    sp = df.at[idx, 'Second Period']
    fpl = df.at[idx,'First Period Location']
    spl = df.at[idx, 'Second Period Location']
    periods = [1,2]
    
    ClassName = [fp, sp]
    ClassLocation = [fpl, spl]
    
    sch_df = pd.DataFrame({'Period' : periods, 'ClassName': ClassName, 
                           'ClassLocation': ClassLocation})  

    return sch_df


# Define my student class(es) in this module while allowing it to act
# as the control program if executed
if __name__ == "__main__":
    
    # Step 0: Initialize students and their data
    df = pd.read_csv("StudentsClasses.csv")
    
    # Generate student schedules from this dataframs
    schedules = {str(idx) : generate_schedule(df, idx) for idx in range(len(df))}
    
    # Instantiate a list of student objects
    students = []
    
    for idx in df.index:
        student_type = df.at[idx, 'Type']
        name = df.at[idx, 'Name']
        current_location = df.at[idx, 'First Period Location'] # Assume it's first period now.
        schedule = schedules[str(idx)]
        
        # Add an Undergrad_student or Grad_studenbt to the list
        if student_type == 'Undergrad':
            students.append(undergrad_student(name, current_location, schedule))
        elif student_type == 'Grad':
            students.append(grad_student(name, current_location, schedule))

    
    # Step 1 and 2: What and where are the classes each student is taking during the next period?
    next_class_names = [student.get_next_classname() for student in students]
    next_class_locations = [student.get_next_period_location() for student in students]
    
    # Step 3: Find the path from my room (the Basket Weaving room, B5-RM210) 
    # to each student's next class.
    instructions_next_class = [student.get_directions_to_classroom(next_class_locations[idx]) for idx, student in enumerate(students)]
    
    # Step 4: Tell the person how to get to the next class
    for idx, student in enumerate(students):
        student.give_instructions(instructions_next_class[idx], next_class_locations[idx])
        print("{} has left {} and arrived at {} for {} class\n---------------------------------".format(
                                                        student.get_name(), "B5-RM210",
                                                        student.get_location(),
                                                        next_class_names[idx]))
    
