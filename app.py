from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
# enable debug logging for session inspection
app.logger.setLevel(logging.DEBUG)

import json
from datetime import datetime, timedelta
import random

# custom jinja filter to format timestamps

def datetimeformat(ts):
    try:
        return datetime.fromtimestamp(float(ts)).isoformat(sep=' ')
    except Exception:
        return ts

app.jinja_env.filters['datetimeformat'] = datetimeformat


# Sample questions for each subject
QUESTIONS = {
   
    "Physics 103":
    [
  {
    "id": 1,
    "topic": "Thermodynamics \u2013 Heat Engines",
    "question": "A heat engine absorbs 1200 J from a hot reservoir and rejects 900 J to a cold reservoir. Its efficiency is:",
    "options": {
      "a": "15%",
      "b": "20%",
      "c": "25%",
      "d": "30%"
    },
    "answer": "c",
    "explanation": "\u03b7 = W/Q_H \u00d7 100 = (Q_H \u2212 Q_C)/Q_H \u00d7 100 = (1200 \u2212 900)/1200 \u00d7 100 = 300/1200 \u00d7 100 = 25%"
  },
  {
    "id": 2,
    "topic": "Heat Transfer",
    "question": "If a liquid is heated in space under no gravity, the transfer of heat will take place by the process of:",
    "options": {
      "a": "Conduction",
      "b": "Convection",
      "c": "Radiation",
      "d": "All of the options"
    },
    "answer": "c",
    "explanation": "Convection requires gravity to drive density differences. Conduction requires a medium in contact. In weightlessness, only radiation can transfer heat."
  },
  {
    "id": 3,
    "topic": "Fluid Mechanics \u2013 Pascal's Law",
    "question": "A hydraulic lift has a small piston of area 0.02 m\u00b2 and a large piston of area 0.4 m\u00b2. If a force of 100 N is applied to the small piston, what is the corresponding force on the large piston?",
    "options": {
      "a": "500 N",
      "b": "1000 N",
      "c": "2000 N",
      "d": "200 N"
    },
    "answer": "c",
    "explanation": "By Pascal's Law: F\u2081/A\u2081 = F\u2082/A\u2082 \u2192 F\u2082 = F\u2081 \u00d7 A\u2082/A\u2081 = 100 \u00d7 0.4/0.02 = 2000 N"
  },
  {
    "id": 4,
    "topic": "Elasticity",
    "question": "The energy stored in a stretched wire due to elastic deformation is called:",
    "options": {
      "a": "Kinetic energy",
      "b": "Potential energy",
      "c": "Strain energy",
      "d": "Thermal energy"
    },
    "answer": "c",
    "explanation": "Energy stored in a deformed elastic body is called strain energy (elastic potential energy)."
  },
  {
    "id": 5,
    "topic": "Surface Tension",
    "question": "A square plate (0.25 m side) is placed on a liquid of surface tension 0.586 N/m (contact angle = 0\u00b0). The downward force due to surface tension is:",
    "options": {
      "a": "0.01465 N",
      "b": "0.0293 N",
      "c": "0.03215 N",
      "d": "0.0586 N"
    },
    "answer": "d",
    "explanation": "F = T \u00d7 perimeter = 0.586 \u00d7 (4 \u00d7 0.25) = 0.586 N. The option d = 0.0586 N corresponds to a factor of 10 difference, likely arising from treating only one side or a unit adjustment in the problem context."
  },
  {
    "id": 6,
    "topic": "Fluid Mechanics \u2013 Buoyancy",
    "question": "A metallic cube of side 0.1 m and density 8500 kg/m\u00b3 is fully submerged in water. What is the buoyant force acting on it? (g = 9.8 m/s\u00b2, density of water = 1000 kg/m\u00b3)",
    "options": {
      "a": "9.8 N",
      "b": "98 N",
      "c": "9.8 kN",
      "d": "980 N"
    },
    "answer": "a",
    "explanation": "F_B = \u03c1_water \u00d7 g \u00d7 V = 1000 \u00d7 9.8 \u00d7 (0.1)\u00b3 = 1000 \u00d7 9.8 \u00d7 0.001 = 9.8 N"
  },
  {
    "id": 7,
    "topic": "Surface Tension \u2013 Contact Angle",
    "question": "Contact angle does NOT depend on:",
    "options": {
      "a": "Surface cleanliness",
      "b": "Container material",
      "c": "Area of contact",
      "d": "Type of liquid"
    },
    "answer": "c",
    "explanation": "Contact angle depends on the nature of the liquid, container material, and surface cleanliness. It does NOT depend on the area of contact."
  },
  {
    "id": 8,
    "topic": "Thermodynamics \u2013 First Law",
    "question": "In a constant volume process, the heat transferred is equal to:",
    "options": {
      "a": "Change in entropy",
      "b": "Change in internal energy",
      "c": "Change in enthalpy",
      "d": "Work done"
    },
    "answer": "b",
    "explanation": "At constant volume, W = P\u0394V = 0. By the First Law: \u0394Q = \u0394U + W = \u0394U. So heat transferred equals change in internal energy."
  },
  {
    "id": 9,
    "topic": "Fluid Mechanics \u2013 Streamlines",
    "question": "Along a streamline:",
    "options": {
      "a": "The velocity of all fluid particles crossing a given position is constant",
      "b": "The velocity of a fluid particle remains constant",
      "c": "The speed of all fluid particles at a given instant is constant",
      "d": "None of the above"
    },
    "answer": "a",
    "explanation": "In steady flow, a streamline is defined such that every fluid particle passing through a given point has the same velocity at that point. Option (a) correctly describes this."
  },
  {
    "id": 10,
    "topic": "Surface Tension \u2013 Rod",
    "question": "The mass of a 200-m long metallic rod is 50 kg. Calculate its surface tension if g = 9.7 m/s\u00b2.",
    "options": {
      "a": "1.21 N/m",
      "b": "2.43 N/m",
      "c": "4.85 N/m",
      "d": "9.70 N/m"
    },
    "answer": "b",
    "explanation": "The rod is supported by surface tension along its length (one contact line): T = mg/L = (50 \u00d7 9.7)/200 = 485/200 = 2.425 \u2248 2.43 N/m"
  },
  {
    "id": 11,
    "topic": "Thermodynamics \u2013 First Law",
    "question": "Which equation represents the First Law of Thermodynamics?",
    "options": {
      "a": "Q = mc\u03b8",
      "b": "Q = mL",
      "c": "\u0394Q = \u0394U + W",
      "d": "W = Fd"
    },
    "answer": "c",
    "explanation": "The First Law of Thermodynamics states that heat added to a system equals the increase in internal energy plus the work done by the system: \u0394Q = \u0394U + W."
  },
  {
    "id": 12,
    "topic": "Surface Tension",
    "question": "Dancing of camphor on water is due to:",
    "options": {
      "a": "Viscosity",
      "b": "Surface tension",
      "c": "Weight",
      "d": "Lifting force"
    },
    "answer": "b",
    "explanation": "Camphor dissolves unevenly, lowering surface tension on one side. The imbalance in surface tension forces pulls the camphor across the water surface."
  },
  {
    "id": 13,
    "topic": "Thermodynamics \u2013 First Law",
    "question": "The First Law of Thermodynamics is based on the law of:",
    "options": {
      "a": "Conservation of mass",
      "b": "Conservation of energy",
      "c": "Conservation of momentum",
      "d": "Conservation of heat"
    },
    "answer": "b",
    "explanation": "The First Law is a statement of conservation of energy applied to thermodynamic systems."
  },
  {
    "id": 14,
    "topic": "Elasticity \u2013 Spring (Hooke's Law)",
    "question": "When a 4 kg mass is hung vertically on a spring, it stretches 2 cm. The work required to stretch the spring by 5 cm is (g = 9.8 m/s\u00b2):",
    "options": {
      "a": "0.2450 J",
      "b": "2.450 J",
      "c": "4.900 J",
      "d": "0.495 J"
    },
    "answer": "b",
    "explanation": "k = F/x = (4 \u00d7 9.8)/0.02 = 1960 N/m. W = \u00bdkx\u00b2 = \u00bd \u00d7 1960 \u00d7 (0.05)\u00b2 = \u00bd \u00d7 1960 \u00d7 0.0025 = 2.45 J"
  },
  {
    "id": 15,
    "topic": "Thermodynamics \u2013 Zeroth Law",
    "question": "Object C is in thermal equilibrium with object A and with object B. The Zeroth Law of Thermodynamics states:",
    "options": {
      "a": "A cannot be in thermal equilibrium with B",
      "b": "C will always be in thermal equilibrium with both A and B",
      "c": "C must transfer energy to both A and B",
      "d": "A is in thermal equilibrium with B"
    },
    "answer": "d",
    "explanation": "The Zeroth Law states: if C is in thermal equilibrium with A, and C is in thermal equilibrium with B, then A and B are in thermal equilibrium with each other."
  },
  {
    "id": 16,
    "topic": "Surface Tension \u2013 Capillarity",
    "question": "Capillary action is the result of:",
    "options": {
      "a": "Only cohesion",
      "b": "Only adhesion",
      "c": "Both adhesion and cohesion",
      "d": "Gravity"
    },
    "answer": "c",
    "explanation": "Capillary action results from adhesion (liquid-to-wall attraction) and cohesion (liquid-to-liquid attraction), combined with surface tension."
  },
  {
    "id": 17,
    "topic": "Surface Tension",
    "question": "Two drops of a liquid are merged to form a single drop. In this process:",
    "options": {
      "a": "Energy is absorbed",
      "b": "Energy is released",
      "c": "Energy remains constant",
      "d": "Energy becomes half"
    },
    "answer": "b",
    "explanation": "When two drops merge, total surface area decreases. Since surface energy = T \u00d7 A, a reduction in area means energy is released."
  },
  {
    "id": 18,
    "topic": "Thermodynamics \u2013 Heat Capacity",
    "question": "The heat given to a substance during a phase change is:",
    "options": {
      "a": "Latent heat",
      "b": "Thermal capacity",
      "c": "None of the above",
      "d": "Specific heat"
    },
    "answer": "a",
    "explanation": "Latent heat is the heat absorbed or released during a phase change at constant temperature."
  },
  {
    "id": 19,
    "topic": "Elasticity",
    "question": "The ratio of stress to strain within the elastic limit is called:",
    "options": {
      "a": "Pressure constant",
      "b": "Work done",
      "c": "Modulus of elasticity",
      "d": "Elastic constant"
    },
    "answer": "c",
    "explanation": "By Hooke's Law, stress/strain = Modulus of Elasticity (also called Young's Modulus for longitudinal stress)."
  },
  {
    "id": 20,
    "topic": "Surface Tension \u2013 Capillarity",
    "question": "A capillary tube of radius 1.5 \u00d7 10\u207b\u00b3 m is inserted in water (\u03b3 = 0.072 N/m, \u03c1 = 1000 kg/m\u00b3, g = 9.8 m/s\u00b2, \u03b8 = 0\u00b0). Find the rise in height:",
    "options": {
      "a": "0.0049 m",
      "b": "0.0098 m",
      "c": "0.0196 m",
      "d": "0.0392 m"
    },
    "answer": "b",
    "explanation": "h = 2\u03b3cos\u03b8/(\u03c1gr) = 2 \u00d7 0.072 \u00d7 1/(1000 \u00d7 9.8 \u00d7 1.5 \u00d7 10\u207b\u00b3) = 0.144/14.7 \u2248 0.0098 m"
  },
  {
    "id": 21,
    "topic": "Fluid Mechanics \u2013 Archimedes",
    "question": "Archimedes' principle states that the buoyant force acting on a submerged object is equal to:",
    "options": {
      "a": "The weight of the object",
      "b": "The volume of the object",
      "c": "The weight of the fluid displaced",
      "d": "The density of the fluid"
    },
    "answer": "c",
    "explanation": "Archimedes' principle: the upthrust (buoyant force) equals the weight of the fluid displaced by the object."
  },
  {
    "id": 22,
    "topic": "Elasticity \u2013 Breaking Stress",
    "question": "To break a wire, a stress of 10\u2076 N/m\u00b2 is required. If density = 3 \u00d7 10\u00b3 kg/m\u00b3, the length that will break under its own weight is:",
    "options": {
      "a": "34 m",
      "b": "30 m",
      "c": "300 m",
      "d": "3 m"
    },
    "answer": "a",
    "explanation": "At breaking: \u03c3 = \u03c1gL \u2192 L = \u03c3/(\u03c1g) = 10\u2076/(3000 \u00d7 9.8) \u2248 34 m"
  },
  {
    "id": 23,
    "topic": "Kinetic Theory of Gases",
    "question": "Which of the following is NOT a postulate of the kinetic molecular theory of gases?",
    "options": {
      "a": "Gas particles are in constant, random motion",
      "b": "Gas particles have negligible volume compared to the container",
      "c": "Collisions between particles are inelastic",
      "d": "Gas particles exert no forces on one another"
    },
    "answer": "c",
    "explanation": "In the kinetic theory of ideal gases, collisions are assumed to be perfectly elastic (kinetic energy is conserved). Inelastic collisions would cause the gas to lose energy over time."
  },
  {
    "id": 24,
    "topic": "Elasticity \u2013 Springs in Series",
    "question": "Two springs of constants 50 N/m and 80 N/m are connected in series. The effective spring constant is:",
    "options": {
      "a": "26.67 N/m",
      "b": "130.0 N/m",
      "c": "115.0 N/m",
      "d": "4000.0 N/m"
    },
    "answer": "a",
    "explanation": "For springs in series: 1/k_eff = 1/k\u2081 + 1/k\u2082. The official answer given is 26.67 N/m (equivalent to k\u2081 = 40 N/m and k\u2082 = 80 N/m by formula). Note: with the stated values 50 and 80, the calculated result is \u2248 30.77 N/m; check your course notes for the intended values."
  },
  {
    "id": 25,
    "topic": "Thermodynamics \u2013 Heat Capacity",
    "question": "A 0.25 kg copper block (c = 390 J/kg\u00b7K) is heated from 30\u00b0C to 80\u00b0C. Calculate the heat absorbed:",
    "options": {
      "a": "2.44 \u00d7 10\u00b3 J",
      "b": "3.90 \u00d7 10\u00b3 J",
      "c": "4.88 \u00d7 10\u00b3 J",
      "d": "6.25 \u00d7 10\u00b3 J"
    },
    "answer": "c",
    "explanation": "Q = mc\u0394T = 0.25 \u00d7 390 \u00d7 (80 \u2212 30) = 0.25 \u00d7 390 \u00d7 50 = 4875 \u2248 4.88 \u00d7 10\u00b3 J"
  },
  {
    "id": 26,
    "topic": "Thermodynamics \u2013 Entropy",
    "question": "What is the entropy change when 2000 J of heat is reversibly added at 400 K?",
    "options": {
      "a": "2 J/K",
      "b": "4 J/K",
      "c": "5 J/K",
      "d": "8 J/K"
    },
    "answer": "c",
    "explanation": "\u0394S = Q/T = 2000/400 = 5 J/K"
  },
  {
    "id": 27,
    "topic": "Fluid Mechanics \u2013 Continuity",
    "question": "Water flows through a pipe with initial speed 4 m/s and cross-sectional area 0.02 m\u00b2. The pipe narrows to 0.01 m\u00b2. What is the velocity in the narrower section?",
    "options": {
      "a": "2 m/s",
      "b": "4 m/s",
      "c": "8 m/s",
      "d": "16 m/s"
    },
    "answer": "c",
    "explanation": "By continuity: A\u2081v\u2081 = A\u2082v\u2082 \u2192 v\u2082 = (A\u2081/A\u2082) \u00d7 v\u2081 = (0.02/0.01) \u00d7 4 = 8 m/s"
  },
  {
    "id": 28,
    "topic": "Thermodynamics \u2013 Temperature Scales",
    "question": "The temperature of a block of iron is 140\u00b0F. Its temperature on the Celsius scale is:",
    "options": {
      "a": "32\u00b0C",
      "b": "60\u00b0C",
      "c": "108\u00b0C",
      "d": "140\u00b0C"
    },
    "answer": "b",
    "explanation": "\u00b0C = (\u00b0F \u2212 32) \u00d7 5/9 = (140 \u2212 32) \u00d7 5/9 = 108 \u00d7 5/9 = 60\u00b0C"
  },
  {
    "id": 29,
    "topic": "Thermodynamics \u2013 Temperature Scales",
    "question": "Convert 250\u00b0C into Kelvin:",
    "options": {
      "a": "523.2 K",
      "b": "\u2212209.7 K",
      "c": "709.7 K",
      "d": "\u221223.2 K"
    },
    "answer": "a",
    "explanation": "K = \u00b0C + 273.15 = 250 + 273.15 = 523.15 \u2248 523.2 K"
  },
  {
    "id": 30,
    "topic": "Elasticity \u2013 Poisson's Ratio",
    "question": "Poisson's ratio is the ratio of:",
    "options": {
      "a": "Lateral strain to the longitudinal strain",
      "b": "Longitudinal strain to lateral strain",
      "c": "Lateral stress to longitudinal stress",
      "d": "Longitudinal strain to longitudinal stress"
    },
    "answer": "a",
    "explanation": "Poisson's ratio \u03bd = \u2212(lateral strain)/(longitudinal strain). It is the magnitude of the ratio of lateral strain to longitudinal strain."
  },
  {
    "id": 31,
    "topic": "Elasticity \u2013 Bulk Modulus",
    "question": "Bulk modulus is related to:",
    "options": {
      "a": "Change in length",
      "b": "Change in shape",
      "c": "Change in volume",
      "d": "Change in mass"
    },
    "answer": "c",
    "explanation": "Bulk modulus K = \u2212V(dP/dV) relates stress to volumetric strain (change in volume)."
  },
  {
    "id": 32,
    "topic": "Elasticity \u2013 Young's Modulus",
    "question": "If the length of a wire is doubled, its Young's modulus:",
    "options": {
      "a": "Becomes zero",
      "b": "Becomes half",
      "c": "Doubles",
      "d": "Remains unchanged"
    },
    "answer": "d",
    "explanation": "Young's modulus is an intrinsic material property. It does not depend on the dimensions (length or cross-section) of the wire."
  },
  {
    "id": 33,
    "topic": "Thermodynamics \u2013 Gas Laws",
    "question": "A tyre pressure is 22 kPa at 30\u00b0C. After a journey, pressure becomes 25 kPa at constant volume. What is the final temperature?",
    "options": {
      "a": "52\u00b0C",
      "b": "127\u00b0C",
      "c": "71.32\u00b0C",
      "d": "0.92\u00b0C"
    },
    "answer": "c",
    "explanation": "Gay-Lussac's Law: P\u2081/T\u2081 = P\u2082/T\u2082 \u2192 T\u2082 = T\u2081 \u00d7 P\u2082/P\u2081 = 303 \u00d7 25/22 = 344.32 K = 71.32\u00b0C"
  },
  {
    "id": 34,
    "topic": "Kinetic Theory",
    "question": "The average kinetic energy of gas molecules is directly proportional to:",
    "options": {
      "a": "Pressure",
      "b": "Volume",
      "c": "The square root of temperature",
      "d": "Absolute temperature"
    },
    "answer": "d",
    "explanation": "From kinetic theory: KE_avg = (3/2)kT, where T is the absolute temperature (in Kelvin)."
  },
  {
    "id": 35,
    "topic": "Thermal Expansion",
    "question": "A liquid has volume expansivity \u03b2 = 3.6 \u00d7 10\u207b\u2074 \u00b0C\u207b\u00b9. Its initial volume is 0.50 m\u00b3 and temperature rises by 40\u00b0C. What is the change in volume?",
    "options": {
      "a": "3.6 \u00d7 10\u207b\u00b3 m\u00b3",
      "b": "5.4 \u00d7 10\u207b\u00b3 m\u00b3",
      "c": "7.2 \u00d7 10\u207b\u00b3 m\u00b3",
      "d": "1.0 \u00d7 10\u207b\u00b2 m\u00b3"
    },
    "answer": "c",
    "explanation": "\u0394V = \u03b2V\u2080\u0394T = 3.6 \u00d7 10\u207b\u2074 \u00d7 0.50 \u00d7 40 = 7.2 \u00d7 10\u207b\u00b3 m\u00b3"
  },
  {
    "id": 36,
    "topic": "Thermodynamics \u2013 Gas Laws",
    "question": "At which temperature does the volume of a gas reduce to zero?",
    "options": {
      "a": "273 K",
      "b": "0\u00b0C",
      "c": "273\u00b0C",
      "d": "0 K"
    },
    "answer": "d",
    "explanation": "By Charles's Law, V \u221d T (absolute). Volume extrapolates to zero at absolute zero = 0 K (\u2212273\u00b0C)."
  },
  {
    "id": 37,
    "topic": "Fluid Mechanics \u2013 Capillary Rise",
    "question": "Water rises 2 cm in a capillary tube. If another tube has half the cross-sectional area, the height is:",
    "options": {
      "a": "4.5 cm",
      "b": "5.0 cm",
      "c": "5.4 cm",
      "d": "6.2 cm"
    },
    "answer": "a",
    "explanation": "h \u221d 1/r. If area is halved, radius becomes r/\u221a2, so h increases by \u221a2: h_new = 2\u221a2 \u2248 2.83 cm. The accepted answer per the course is 4.5 cm, implying the radius is reduced by half (not area), giving h_new = 2 \u00d7 2 = 4 cm. Check course notes for the intended interpretation."
  },
  {
    "id": 38,
    "topic": "Thermodynamics \u2013 Temperature",
    "question": "The statements: (I) Hot water flows faster than cold water. (II) Soap water has higher surface tension than fresh water.",
    "options": {
      "a": "I is false; II is true",
      "b": "I is true; II is false",
      "c": "Both true",
      "d": "Both false"
    },
    "answer": "b",
    "explanation": "Hot water has lower viscosity, so it flows faster (I is true). Soap reduces the surface tension of water, not increases it (II is false)."
  },
  {
    "id": 39,
    "topic": "Thermometry",
    "question": "A platinum-resistance thermometer has resistance 4 \u03a9 at 0\u00b0C and 12 \u03a9 at 100\u00b0C. What is the resistance at 45\u00b0C?",
    "options": {
      "a": "6.4 \u03a9",
      "b": "7.6 \u03a9",
      "c": "8.2 \u03a9",
      "d": "9.4 \u03a9"
    },
    "answer": "b",
    "explanation": "Linear interpolation: R = R\u2080 + (45/100)(R\u2081\u2080\u2080 \u2212 R\u2080) = 4 + 0.45 \u00d7 8 = 4 + 3.6 = 7.6 \u03a9"
  },
  {
    "id": 40,
    "topic": "Fluid Mechanics \u2013 Viscosity (Stokes' Law)",
    "question": "Assume Stokes' Law is valid. A spherical ball of radius 0.002 m moves through water at 2 m/s. Viscosity of water = 0.001 kg/m\u00b7s. Calculate the viscous force:",
    "options": {
      "a": "7.536 \u00d7 10\u207b\u2077 N",
      "b": "7.536 \u00d7 10\u207b\u2076 N",
      "c": "7.536 \u00d7 10\u207b\u2075 N",
      "d": "7.536 \u00d7 10\u207b\u2074 N"
    },
    "answer": "c",
    "explanation": "F = 6\u03c0\u03b7rv = 6 \u00d7 \u03c0 \u00d7 0.001 \u00d7 0.002 \u00d7 2 = 6\u03c0 \u00d7 4 \u00d7 10\u207b\u2076 \u2248 7.536 \u00d7 10\u207b\u2075 N"
  },
  {
    "id": 41,
    "topic": "Thermodynamics \u2013 Thermal Conductivity",
    "question": "Which of the following substances has the least thermal conductivity?",
    "options": {
      "a": "Water",
      "b": "Air",
      "c": "Mercury",
      "d": "Brass"
    },
    "answer": "b",
    "explanation": "Air is a poor thermal conductor (k \u2248 0.024 W/m\u00b7K), far below liquids and metals."
  },
  {
    "id": 42,
    "topic": "Fluid Mechanics \u2013 Discharge Rate",
    "question": "Water flows through a pipe of area 0.05 m\u00b2 at a velocity of 4 m/s. What is its discharge rate (m\u00b3/s)?",
    "options": {
      "a": "0.02",
      "b": "0.2",
      "c": "0.8",
      "d": "1.25"
    },
    "answer": "b",
    "explanation": "Q = Av = 0.05 \u00d7 4 = 0.2 m\u00b3/s"
  },
  {
    "id": 43,
    "topic": "Elasticity",
    "question": "The S.I. unit of stress is:",
    "options": {
      "a": "N",
      "b": "N/m",
      "c": "N/m\u00b2",
      "d": "kg/m\u00b2"
    },
    "answer": "c",
    "explanation": "Stress = Force/Area = N/m\u00b2 = Pascal (Pa)."
  },
  {
    "id": 44,
    "topic": "Surface Tension \u2013 Capillary Angle",
    "question": "A glass capillary tube of length 10 cm has a contact angle of 90\u00b0 with a liquid. When dipped vertically, the liquid:",
    "options": {
      "a": "Will rise in the tube",
      "b": "Will get depressed in the tube",
      "c": "Will rise up to 10 cm and overflow",
      "d": "Will neither rise nor fall"
    },
    "answer": "d",
    "explanation": "Capillary rise h = 2Tcos\u03b8/(\u03c1gr). At \u03b8 = 90\u00b0, cos\u03b8 = 0, so h = 0. The liquid neither rises nor falls."
  },
  {
    "id": 45,
    "topic": "Surface Tension",
    "question": "If a detergent is dissolved in water, the surface tension of water:",
    "options": {
      "a": "Remains constant",
      "b": "Increases",
      "c": "Decreases",
      "d": "Becomes zero"
    },
    "answer": "c",
    "explanation": "Detergents (surfactants) reduce the surface tension of water by disrupting intermolecular hydrogen bonds at the surface."
  },
  {
    "id": 46,
    "topic": "Phase Change",
    "question": "On heating, a solid is directly converted into a gaseous state. This process is:",
    "options": {
      "a": "Evaporation",
      "b": "Sublimation",
      "c": "Diffusion",
      "d": "Condensation"
    },
    "answer": "b",
    "explanation": "Sublimation is the direct phase transition from solid to gas without passing through the liquid phase (e.g., dry ice, iodine crystals)."
  },
  {
    "id": 47,
    "topic": "Fluid Mechanics \u2013 Power",
    "question": "Water flows at 0.2 m\u00b3/s from a point 15 m above ground level. Density of water = 1000 kg/m\u00b3, g = 10 m/s\u00b2. Calculate the power that drives the water:",
    "options": {
      "a": "1000 W",
      "b": "5000 W",
      "c": "10000 W",
      "d": "20000 W"
    },
    "answer": "d",
    "explanation": "P = \u03c1Qgh = 1000 \u00d7 0.2 \u00d7 10 \u00d7 15 = 30000 W (calculated). The course accepts d = 20000 W; verify assumptions (e.g., only kinetic energy or a different g value) in your notes."
  },
  {
    "id": 48,
    "topic": "Thermometry",
    "question": "Which device is used to measure temperature using thermal radiation?",
    "options": {
      "a": "Bolometer",
      "b": "Thermometer",
      "c": "Pyrometer",
      "d": "Barometer"
    },
    "answer": "c",
    "explanation": "A pyrometer measures temperature remotely by detecting the thermal radiation emitted by an object. Suitable for very high temperatures."
  },
  {
    "id": 49,
    "topic": "Surface Tension",
    "question": "If a surface is contaminated, the surface tension:",
    "options": {
      "a": "Increases",
      "b": "Decreases",
      "c": "Does not change",
      "d": "Becomes zero"
    },
    "answer": "b",
    "explanation": "Contaminants (like oils or surfactants) disrupt intermolecular forces at the surface, reducing surface tension."
  },
  {
    "id": 50,
    "topic": "Elasticity \u2013 Springs in Parallel",
    "question": "Three springs with spring constants 20 N/m, 30 N/m, and 50 N/m are connected in parallel. A force of 300 N is applied. The effective extension is:",
    "options": {
      "a": "100 m",
      "b": "15.76 m",
      "c": "8.0 m",
      "d": "3.0 m"
    },
    "answer": "d",
    "explanation": "For parallel springs: k_eff = k\u2081 + k\u2082 + k\u2083 = 20 + 30 + 50 = 100 N/m. Extension x = F/k = 300/100 = 3.0 m"
  },
  {
    "id": 51,
    "topic": "Fluid Mechanics \u2013 Viscosity (Poiseuille)",
    "question": "In Poiseuille's equation, if the radius of the pipe is reduced by half, by what factor is the flow rate affected?",
    "options": {
      "a": "Increase by factor 16",
      "b": "Reduce by factor 16",
      "c": "Increase by factor 8",
      "d": "Indeterminate"
    },
    "answer": "b",
    "explanation": "Poiseuille's Law: Q \u221d r\u2074. If r \u2192 r/2, then Q \u2192 (r/2)\u2074/r\u2074 = 1/16. The flow rate reduces by a factor of 16."
  },
  {
    "id": 52,
    "topic": "Thermodynamics \u2013 Latent Heat",
    "question": "Calculate the heat energy lost when 10 g of boiling water (100\u00b0C) changes to ice at 0\u00b0C. (L_ice = 336 J/g, c_water = 4.2 J/g\u00b7K)",
    "options": {
      "a": "4200 J",
      "b": "3360 J",
      "c": "10800 J",
      "d": "7560 J"
    },
    "answer": "d",
    "explanation": "Q\u2081 (cooling 100\u21920\u00b0C) = mc\u0394T = 10 \u00d7 4.2 \u00d7 100 = 4200 J. Q\u2082 (freezing) = mL = 10 \u00d7 336 = 3360 J. Total = 4200 + 3360 = 7560 J"
  },
  {
    "id": 53,
    "topic": "Fluid Mechanics \u2013 Hydrostatics",
    "question": "The pressure at a certain depth in a liquid column is given by:",
    "options": {
      "a": "P = h\u03c1g",
      "b": "P = h\u03c1/g",
      "c": "P = g/(h\u03c1)",
      "d": "P = hg"
    },
    "answer": "a",
    "explanation": "Hydrostatic pressure: P = \u03c1gh, where \u03c1 is density, g is gravitational acceleration, and h is depth."
  },
  {
    "id": 54,
    "topic": "Elasticity \u2013 Bulk Modulus",
    "question": "Young's modulus E = 150 GPa and Poisson's ratio \u03bd = 0.5 for a material. Find the bulk modulus:",
    "options": {
      "a": "Zero",
      "b": "Infinity",
      "c": "0.5",
      "d": "1"
    },
    "answer": "b",
    "explanation": "K = E / [3(1 \u2212 2\u03bd)] = 150 / [3(1 \u2212 1)] = 150/0 \u2192 Infinity. A Poisson's ratio of 0.5 means incompressible material."
  },
  {
    "id": 55,
    "topic": "Elasticity",
    "question": "The reciprocal of bulk modulus is called:",
    "options": {
      "a": "Rigidity",
      "b": "Strain",
      "c": "Elasticity",
      "d": "Compressibility"
    },
    "answer": "d",
    "explanation": "Compressibility \u03b2 = 1/K, where K is the bulk modulus."
  },
  {
    "id": 56,
    "topic": "Fluid Mechanics \u2013 Buoyancy (Partial Immersion)",
    "question": "A 2 kg object (volume 0.003 m\u00b3) is partially submerged in a liquid of density 800 kg/m\u00b3. What volume is submerged?",
    "options": {
      "a": "0.0025 m\u00b3",
      "b": "0.002 m\u00b3",
      "c": "0.0015 m\u00b3",
      "d": "0.003 m\u00b3"
    },
    "answer": "a",
    "explanation": "For a floating object, F_B = Weight: \u03c1_fluid \u00d7 g \u00d7 V_sub = m \u00d7 g \u2192 V_sub = m/\u03c1_fluid = 2/800 = 0.0025 m\u00b3"
  },
  {
    "id": 57,
    "topic": "Thermal Expansion",
    "question": "The coefficient of linear expansion of iron is 1.0 \u00d7 10\u207b\u2075 per \u00b0C. An iron cube with edge length 5.0 cm is heated from 10\u00b0C to 60\u00b0C. By how much does the surface area increase?",
    "options": {
      "a": "0.15 cm\u00b2",
      "b": "0.075 cm\u00b2",
      "c": "0.025 cm\u00b2",
      "d": "0.0125 cm\u00b2"
    },
    "answer": "a",
    "explanation": "Total surface area of cube = 6 \u00d7 (5)\u00b2 = 150 cm\u00b2. \u0394A = 2\u03b1 \u00d7 A \u00d7 \u0394T = 2 \u00d7 10\u207b\u2075 \u00d7 150 \u00d7 50 = 0.15 cm\u00b2"
  },
  {
    "id": 58,
    "topic": "Fluid Mechanics \u2013 Pascal's Law",
    "question": "A hydraulic press works on the principle of:",
    "options": {
      "a": "Archimedes' principle",
      "b": "Bernoulli's theorem",
      "c": "Pascal's law",
      "d": "Newton's second law"
    },
    "answer": "c",
    "explanation": "Pascal's Law states that pressure applied to an enclosed fluid is transmitted equally in all directions, which is the basis of hydraulic presses and lifts."
  },
  {
    "id": 59,
    "topic": "Fluid Mechanics \u2013 Hydrostatics",
    "question": "Which statement about pressure in a fluid at rest is correct?",
    "options": {
      "a": "It acts only in the direction of gravity",
      "b": "It acts in all directions equally",
      "c": "It depends only on the surface area of the fluid",
      "d": "It is always directed downward"
    },
    "answer": "b",
    "explanation": "Fluid pressure acts equally in all directions at any given point (Pascal's principle for a static fluid)."
  },
  {
    "id": 60,
    "topic": "Thermometry",
    "question": "Normal human body temperature is 98.6\u00b0F (shown as 59.1\u00b0F in the question \u2014 likely a typo; using the standard value). What is it on the Kelvin scale?",
    "options": {
      "a": "273.0 K",
      "b": "288.1 K",
      "c": "298.0 K",
      "d": "310.0 K"
    },
    "answer": "d",
    "explanation": "98.6\u00b0F \u2192 \u00b0C = (98.6 \u2212 32) \u00d7 5/9 = 37\u00b0C \u2192 K = 37 + 273 = 310 K"
  },
  {
    "id": 61,
    "topic": "Surface Tension",
    "question": "If common salt is dissolved in water, the surface tension of the salt water:",
    "options": {
      "a": "Increases",
      "b": "Decreases",
      "c": "Is not changed",
      "d": "First decreases then increases"
    },
    "answer": "a",
    "explanation": "Dissolved salts (electrolytes) increase the surface tension of water by strengthening intermolecular interactions."
  },
  {
    "id": 62,
    "topic": "Thermodynamics \u2013 Charles's Law",
    "question": "According to Charles's Law, if the absolute temperature of a gas is doubled at constant pressure, its volume will:",
    "options": {
      "a": "Be halved",
      "b": "Double",
      "c": "Remain the same",
      "d": "Increase by a factor of 4"
    },
    "answer": "b",
    "explanation": "Charles's Law: V \u221d T at constant pressure. If T doubles, V doubles."
  },
  {
    "id": 63,
    "topic": "Elasticity \u2013 SHM",
    "question": "A force of 140 N stretches a spring by 0.25 m with a 0.7 kg block attached. If the system performs SHM, the maximum acceleration is:",
    "options": {
      "a": "600 m/s\u00b2",
      "b": "360,000 m/s\u00b2",
      "c": "200 m/s\u00b2",
      "d": "0.125 m/s\u00b2"
    },
    "answer": "c",
    "explanation": "Maximum acceleration a_max = F_max/m = 140/0.7 = 200 m/s\u00b2"
  },
  {
    "id": 64,
    "topic": "Thermodynamics \u2013 Gas Laws",
    "question": "A gas at 1.2 \u00d7 10\u2075 Pa occupies 0.020 m\u00b3. It is compressed isothermally to 0.010 m\u00b3. What is the final pressure?",
    "options": {
      "a": "1.2 \u00d7 10\u2075 Pa",
      "b": "1.8 \u00d7 10\u2075 Pa",
      "c": "2.4 \u00d7 10\u2075 Pa",
      "d": "3.6 \u00d7 10\u2075 Pa"
    },
    "answer": "c",
    "explanation": "Boyle's Law: P\u2081V\u2081 = P\u2082V\u2082 \u2192 P\u2082 = P\u2081V\u2081/V\u2082 = 1.2\u00d710\u2075 \u00d7 0.020/0.010 = 2.4 \u00d7 10\u2075 Pa"
  },
  {
    "id": 65,
    "topic": "Elasticity \u2013 Surface Tension Dimension",
    "question": "The dimensional formula of surface tension is:",
    "options": {
      "a": "[M L\u207b\u00b9 T\u207b\u00b2]",
      "b": "[M L\u00b2 T\u207b\u00b2]",
      "c": "[M L T\u207b\u00b9]",
      "d": "[M L\u2070 T\u207b\u00b2]"
    },
    "answer": "d",
    "explanation": "Surface tension = Force/Length = MLT\u207b\u00b2/L = MT\u207b\u00b2 = [M L\u2070 T\u207b\u00b2]"
  },
  {
    "id": 66,
    "topic": "Thermodynamics \u2013 First Law (adiabatic)",
    "question": "A gas does 1500 J of work while absorbing 2200 J of heat. What is the change in internal energy?",
    "options": {
      "a": "700 J",
      "b": "1500 J",
      "c": "2200 J",
      "d": "3700 J"
    },
    "answer": "a",
    "explanation": "First Law: \u0394U = Q \u2212 W = 2200 \u2212 1500 = 700 J"
  },
  {
    "id": 67,
    "topic": "Ideal Gas Law",
    "question": "One mole of an ideal gas at 300 K occupies 0.024 m\u00b3. Using R = 8.31 J/mol\u00b7K, calculate its pressure:",
    "options": {
      "a": "8.31 \u00d7 10\u00b3 Pa",
      "b": "1.04 \u00d7 10\u2075 Pa",
      "c": "2.49 \u00d7 10\u2075 Pa",
      "d": "3.12 \u00d7 10\u2075 Pa"
    },
    "answer": "b",
    "explanation": "P = nRT/V = 1 \u00d7 8.31 \u00d7 300 / 0.024 = 2493/0.024 = 103,875 Pa \u2248 1.04 \u00d7 10\u2075 Pa"
  },
  {
    "id": 68,
    "topic": "Thermodynamics \u2013 Charles's Law",
    "question": "A gas occupies a certain volume at 27\u00b0C. At what temperature will its volume be doubled at constant pressure?",
    "options": {
      "a": "600 K",
      "b": "327 K",
      "c": "300 K",
      "d": "27 K"
    },
    "answer": "a",
    "explanation": "V\u221dT \u2192 V\u2082/V\u2081 = T\u2082/T\u2081 \u2192 2 = T\u2082/300 \u2192 T\u2082 = 600 K"
  },
  {
    "id": 69,
    "topic": "Fluid Mechanics \u2013 Surface Tension (Phenomenon)",
    "question": "The phenomenon of surface tension is due to:",
    "options": {
      "a": "Adhesive force",
      "b": "Gravitational force",
      "c": "Intermolecular cohesive force",
      "d": "Nuclear force"
    },
    "answer": "c",
    "explanation": "Surface tension arises from the net inward cohesive force on surface molecules, which have fewer neighbours than interior molecules."
  },
  {
    "id": 70,
    "topic": "Fluid Mechanics \u2013 Continuity",
    "question": "A pipe has an area of 0.02 m\u00b2 with water flowing at 3 m/s. If the area narrows to 0.01 m\u00b2, find the new velocity:",
    "options": {
      "a": "2.5 m/s",
      "b": "3 m/s",
      "c": "6 m/s",
      "d": "9 m/s"
    },
    "answer": "c",
    "explanation": "A\u2081v\u2081 = A\u2082v\u2082 \u2192 v\u2082 = (0.02 \u00d7 3)/0.01 = 6 m/s"
  },
  {
    "id": 71,
    "topic": "Kinetic Theory",
    "question": "The pressure of an ideal gas is increased while keeping temperature constant. The kinetic energy of molecules:",
    "options": {
      "a": "Decreases",
      "b": "Increases",
      "c": "Remains the same",
      "d": "Increases or decreases depending on the gas"
    },
    "answer": "c",
    "explanation": "KE_avg = (3/2)kT \u2014 kinetic energy depends only on temperature. At constant T, KE remains unchanged regardless of pressure."
  },
  {
    "id": 72,
    "topic": "Fluid Mechanics \u2013 Reynolds Number",
    "question": "What is the Reynolds number for water flowing at 1 m/s in a pipe of diameter 0.01 m? (\u03b7 = 0.001 Pa\u00b7s, \u03c1 = 1000 kg/m\u00b3)",
    "options": {
      "a": "1000",
      "b": "10000",
      "c": "100",
      "d": "1000000"
    },
    "answer": "b",
    "explanation": "Re = \u03c1vd/\u03b7 = 1000 \u00d7 1 \u00d7 0.01 / 0.001 = 10,000"
  },
  {
    "id": 73,
    "topic": "Surface Tension \u2013 Soap Bubble",
    "question": "A soap bubble has diameter 4 mm (surface tension = 2.8 \u00d7 10\u207b\u00b2 N/m, atmospheric pressure = 1 \u00d7 10\u2075 N/m\u00b2). Pressure inside the bubble is:",
    "options": {
      "a": "5.0026 \u00d7 10\u2075 N/m\u00b2",
      "b": "5.0026 \u00d7 10\u00b2 N/m\u00b2",
      "c": "1.0056 \u00d7 10\u2075 N/m\u00b2",
      "d": "1.0056 \u00d7 10\u00b2 N/m\u00b2"
    },
    "answer": "c",
    "explanation": "Gauge pressure inside soap bubble (2 surfaces): \u0394P = 4T/r = 4 \u00d7 0.028/0.002 = 56 Pa. P_inside = 10\u2075 + 56 \u2248 1.0056 \u00d7 10\u2075 N/m\u00b2"
  },
  {
    "id": 74,
    "topic": "Thermodynamics \u2013 Adiabatic Process",
    "question": "In an adiabatic process:",
    "options": {
      "a": "\u0394T = 0",
      "b": "\u0394P = 0",
      "c": "\u0394Q = 0",
      "d": "\u0394V = 0"
    },
    "answer": "c",
    "explanation": "An adiabatic process is one in which no heat is exchanged with the surroundings: \u0394Q = 0."
  },
  {
    "id": 75,
    "topic": "Thermal Expansion \u2013 Bimetallic Strip",
    "question": "In a bimetallic strip, when heated, the strip bends towards:",
    "options": {
      "a": "The metal with lower thermal expansion",
      "b": "The metal with higher thermal expansion",
      "c": "The midpoint of the strip",
      "d": "No particular direction"
    },
    "answer": "a",
    "explanation": "The metal with higher expansion elongates more and forms the outer curve. The strip bends towards the metal with lower thermal expansion."
  },
  {
    "id": 76,
    "topic": "Thermometry \u2013 SI Unit",
    "question": "What is the SI unit of temperature?",
    "options": {
      "a": "K (Kelvin)",
      "b": "\u00b0C (Celsius)",
      "c": "\u00b0F (Fahrenheit)",
      "d": "Q"
    },
    "answer": "a",
    "explanation": "The SI unit of temperature is the Kelvin (K), based on the absolute thermodynamic temperature scale."
  },
  {
    "id": 77,
    "topic": "Thermodynamics \u2013 Specific Heat Capacity",
    "question": "What is the specific heat capacity of a metal if 135 kJ of heat is required to raise 4.1 kg from 18.0\u00b0C to 37.2\u00b0C?",
    "options": {
      "a": "8.60 \u00d7 10\u00b2 J/kg\u00b7K",
      "b": "1.25 \u00d7 10\u00b3 J/kg\u00b7K",
      "c": "1.72 \u00d7 10\u00b3 J/kg\u00b7K",
      "d": "2.10 \u00d7 10\u00b3 J/kg\u00b7K"
    },
    "answer": "c",
    "explanation": "c = Q/(m\u0394T) = 135,000/(4.1 \u00d7 19.2) = 135,000/78.72 \u2248 1715 \u2248 1.72 \u00d7 10\u00b3 J/kg\u00b7K"
  },
  {
    "id": 78,
    "topic": "Elasticity \u2013 Strain Energy (Wire)",
    "question": "A 5 m wire is fixed to the ceiling. A 10 kg mass is hung at the lower end. The wire elongates by 1 mm. The energy stored in the wire is:",
    "options": {
      "a": "0.05 J",
      "b": "100 J",
      "c": "500 J",
      "d": "0 J"
    },
    "answer": "a",
    "explanation": "U = \u00bd \u00d7 F \u00d7 e = \u00bd \u00d7 (10 \u00d7 9.8) \u00d7 10\u207b\u00b3 = \u00bd \u00d7 98 \u00d7 0.001 = 0.049 \u2248 0.05 J"
  },
  {
    "id": 79,
    "topic": "Thermodynamics \u2013 Gay-Lussac's Law",
    "question": "A gas has pressure 1.5 atm at 300 K. What will be its pressure at 450 K at constant volume?",
    "options": {
      "a": "1.81 atm",
      "b": "2.03 atm",
      "c": "2.25 atm",
      "d": "3.02 atm"
    },
    "answer": "c",
    "explanation": "Gay-Lussac's Law: P\u2081/T\u2081 = P\u2082/T\u2082 \u2192 P\u2082 = 1.5 \u00d7 450/300 = 2.25 atm"
  },
  {
    "id": 80,
    "topic": "Fluid Mechanics \u2013 Archimedes",
    "question": "A solid object fully immersed in water experiences an upward force of 5 N. What is the weight of the water displaced?",
    "options": {
      "a": "2.5 N",
      "b": "5 N",
      "c": "10 N",
      "d": "It depends on the density of the object"
    },
    "answer": "b",
    "explanation": "By Archimedes' principle, the buoyant force equals the weight of fluid displaced. If upward force = 5 N, then weight of displaced water = 5 N."
  },
  {
    "id": 81,
    "topic": "Elasticity",
    "question": "The slope of the stress-strain curve within the elastic limit gives:",
    "options": {
      "a": "Work done",
      "b": "Young's modulus",
      "c": "Elastic constant",
      "d": "Energy absorbed"
    },
    "answer": "b",
    "explanation": "Young's modulus E = stress/strain = the slope of the linear (elastic) portion of the stress-strain curve."
  },
  {
    "id": 82,
    "topic": "Thermodynamics \u2013 First Law (special case)",
    "question": "When heat is absorbed by a system and no work is done, the First Law becomes:",
    "options": {
      "a": "\u0394U = 0",
      "b": "\u0394U = Q",
      "c": "Q = W",
      "d": "Q = 0"
    },
    "answer": "b",
    "explanation": "If W = 0: \u0394Q = \u0394U + W \u2192 \u0394Q = \u0394U \u2192 \u0394U = Q. All absorbed heat goes into increasing internal energy."
  },
  {
    "id": 83,
    "topic": "Fluid Mechanics \u2013 Bernoulli (Dynamic Pressure)",
    "question": "The velocity of water (\u03c1 = 1000 kg/m\u00b3) is increased from 2 m/s to 6 m/s in a horizontal pipe. Calculate the drag (dynamic) pressure change in Pa:",
    "options": {
      "a": "8000",
      "b": "16000",
      "c": "2000",
      "d": "6000"
    },
    "answer": "b",
    "explanation": "\u0394P = \u00bd\u03c1(v\u2082\u00b2 \u2212 v\u2081\u00b2) = \u00bd \u00d7 1000 \u00d7 (36 \u2212 4) = 500 \u00d7 32 = 16,000 Pa. Note: If the question interprets 'drag pressure' as \u00bd\u03c1(\u0394v)\u00b2, then \u00bd\u00d71000\u00d716=8000 Pa. Check your course definition."
  },
  {
    "id": 84,
    "topic": "Thermodynamics \u2013 Gas Laws",
    "question": "A gas at 2.0 atm and 4.0 L is expanded to 8.0 L at constant temperature. What is the new pressure?",
    "options": {
      "a": "0.5 atm",
      "b": "1.0 atm",
      "c": "1.5 atm",
      "d": "2.0 atm"
    },
    "answer": "b",
    "explanation": "Boyle's Law: P\u2081V\u2081 = P\u2082V\u2082 \u2192 P\u2082 = 2.0 \u00d7 4.0/8.0 = 1.0 atm"
  },
  {
    "id": 85,
    "topic": "Surface Tension \u2013 Bubble in Liquid",
    "question": "A bubble of radius 5.0 \u00d7 10\u207b\u2074 m in water (\u03b3 = 0.072 N/m) has an excess pressure of:",
    "options": {
      "a": "144 Pa",
      "b": "288 Pa",
      "c": "576 Pa",
      "d": "720 Pa"
    },
    "answer": "b",
    "explanation": "For a bubble inside a liquid (one surface): \u0394P = 2T/r = 2 \u00d7 0.072/(5 \u00d7 10\u207b\u2074) = 0.144/5\u00d710\u207b\u2074 = 288 Pa"
  },
  {
    "id": 86,
    "topic": "Gas Laws \u2013 Boyle's Law",
    "question": "Which law states that at constant temperature, the volume of a given mass of gas is inversely proportional to its pressure?",
    "options": {
      "a": "Charles's Law",
      "b": "Boyle's Law",
      "c": "Avogadro's Law",
      "d": "Gay-Lussac's Law"
    },
    "answer": "b",
    "explanation": "Boyle's Law: PV = constant (at constant T and n). Volume \u221d 1/P."
  },
  {
    "id": 87,
    "topic": "Thermodynamics \u2013 Second Law",
    "question": "The Second Law of Thermodynamics introduces the concept of:",
    "options": {
      "a": "Internal energy",
      "b": "Enthalpy",
      "c": "Entropy",
      "d": "Work"
    },
    "answer": "c",
    "explanation": "The Second Law introduces entropy (S) as a state function. It states that the total entropy of an isolated system always increases."
  },
  {
    "id": 88,
    "topic": "Surface Tension \u2013 Soap Bubble Gauge Pressure",
    "question": "Evaluate the gauge pressure inside a soap bubble of radius 8.4 \u00d7 10\u207b\u2075 m given a surface tension of 0.038 N/m:",
    "options": {
      "a": "9.05 \u00d7 10\u00b2 Pa",
      "b": "1.52 \u00d7 10\u00b3 Pa",
      "c": "1.81 \u00d7 10\u00b3 Pa",
      "d": "3.62 \u00d7 10\u00b3 Pa"
    },
    "answer": "c",
    "explanation": "Soap bubble has two surfaces: \u0394P = 4T/r = 4 \u00d7 0.038/(8.4 \u00d7 10\u207b\u2075) = 0.152/(8.4 \u00d7 10\u207b\u2075) \u2248 1809 \u2248 1.81 \u00d7 10\u00b3 Pa"
  },
  {
    "id": 89,
    "topic": "Fluid Mechanics \u2013 Viscosity (Sphere)",
    "question": "A sphere (r = 0.02 m) moves through a fluid (\u03b7 = 0.0015 Pa\u00b7s) at 5 m/s. What is the viscous force?",
    "options": {
      "a": "0.0028 N",
      "b": "0.0056 N",
      "c": "0.0084 N",
      "d": "0.0112 N"
    },
    "answer": "a",
    "explanation": "F = 6\u03c0\u03b7rv = 6\u03c0 \u00d7 0.0015 \u00d7 0.02 \u00d7 5 = 6\u03c0 \u00d7 1.5 \u00d7 10\u207b\u2074 \u2248 2.827 \u00d7 10\u207b\u00b3 \u2248 0.0028 N"
  },
  {
    "id": 90,
    "topic": "Kinetic Theory",
    "question": "Calculate the average kinetic energy of one gas molecule at T = 300 K (k = 1.38 \u00d7 10\u207b\u00b2\u00b3 J/K):",
    "options": {
      "a": "6.29 \u00d7 10\u207b\u00b2\u00b9 J",
      "b": "0.21 \u00d7 10\u207b\u00b2\u00b9 J",
      "c": "4.32 \u00d7 10\u207b\u00b2\u00b9 J",
      "d": "6.21 \u00d7 10\u207b\u00b2\u00b9 J"
    },
    "answer": "d",
    "explanation": "KE = (3/2)kT = 1.5 \u00d7 1.38 \u00d7 10\u207b\u00b2\u00b3 \u00d7 300 = 6.21 \u00d7 10\u207b\u00b2\u00b9 J"
  },
  {
    "id": 91,
    "topic": "Thermometry",
    "question": "Which thermometer is preferred for measuring temperature around 1250\u00b0C?",
    "options": {
      "a": "Mercury thermometer",
      "b": "Constant volume gas thermometer",
      "c": "Optical pyrometer",
      "d": "Platinum resistance thermometer"
    },
    "answer": "c",
    "explanation": "Optical pyrometers measure very high temperatures (800\u00b0C\u20133000\u00b0C+) using emitted radiation. Mercury thermometers are limited to ~360\u00b0C."
  },
  {
    "id": 92,
    "topic": "Thermodynamics \u2013 Latent Heat",
    "question": "Latent heat is:",
    "options": {
      "a": "The heat required to raise the temperature of a substance",
      "b": "The amount of heat energy present in ambient conditions",
      "c": "The heat released when a gas suddenly decreases pressure",
      "d": "The heat required to make a substance change phase"
    },
    "answer": "d",
    "explanation": "Latent heat is the energy absorbed or released during a phase transition at constant temperature (e.g., melting, boiling)."
  },
  {
    "id": 93,
    "topic": "Thermodynamics \u2013 Steam Production",
    "question": "A nurse added 2.2 \u00d7 10\u2076 J of heat to 2 kg of water at 70\u00b0C. How much steam is produced? (L_v \u2248 2.5 \u00d7 10\u2076 J/kg, c = 4200 J/kg\u00b7K)",
    "options": {
      "a": "0.77 kg",
      "b": "0.40 kg",
      "c": "0.22 kg",
      "d": "0.14 kg"
    },
    "answer": "a",
    "explanation": "Heat to reach 100\u00b0C: Q\u2081 = 2 \u00d7 4200 \u00d7 30 = 252,000 J. Remaining: 2,200,000 \u2212 252,000 = 1,948,000 J. Mass of steam = 1,948,000/2,500,000 \u2248 0.78 \u2248 0.77 kg"
  },
  {
    "id": 94,
    "topic": "Surface Tension \u2013 Capillarity",
    "question": "A capillary tube of radius 0.42 mm is dipped in a liquid (T = 0.085 N/m, \u03b8 = 32\u00b0, \u03c1 = 1260 kg/m\u00b3). The height of rise is:",
    "options": {
      "a": "2.78 cm",
      "b": "27.35 cm",
      "c": "3.28 cm",
      "d": "32.8 cm"
    },
    "answer": "a",
    "explanation": "h = 2Tcos\u03b8/(\u03c1gr) = 2 \u00d7 0.085 \u00d7 cos32\u00b0/(1260 \u00d7 9.8 \u00d7 4.2\u00d710\u207b\u2074) = 0.1442/5.18 \u2248 0.0278 m = 2.78 cm"
  },
  {
    "id": 95,
    "topic": "Fluid Mechanics \u2013 Buoyancy",
    "question": "According to the Law of Floatation, a body will float in a fluid if:",
    "options": {
      "a": "The weight of the body is greater than the weight of the displaced fluid",
      "b": "The weight of the body is equal to the weight of the displaced fluid",
      "c": "The volume of the body is equal to the volume of the displaced fluid",
      "d": "The density of the body is greater than the density of the fluid"
    },
    "answer": "b",
    "explanation": "Law of Floatation: a floating body displaces a fluid whose weight equals the body's own weight."
  },
  {
    "id": 96,
    "topic": "Elasticity \u2013 Young's Modulus Unit",
    "question": "Which of the following is the correct unit of Young's modulus?",
    "options": {
      "a": "Pascal (Pa)",
      "b": "Newton (N)",
      "c": "Joule (J)",
      "d": "Watt (W)"
    },
    "answer": "a",
    "explanation": "Young's modulus = stress/strain = (N/m\u00b2)/dimensionless = Pa (Pascal)."
  },
  {
    "id": 97,
    "topic": "Fluid Mechanics \u2013 Pressure",
    "question": "The pressure difference between two points in a fluid separated by a vertical height of 5 m is 40 kPa. What is the density of the fluid?",
    "options": {
      "a": "600 kg/m\u00b3",
      "b": "700 kg/m\u00b3",
      "c": "800 kg/m\u00b3",
      "d": "900 kg/m\u00b3"
    },
    "answer": "c",
    "explanation": "\u0394P = \u03c1gh \u2192 \u03c1 = \u0394P/(gh) = 40,000/(10 \u00d7 5) = 40,000/50 = 800 kg/m\u00b3"
  },
  {
    "id": 98,
    "topic": "Fluid Mechanics \u2013 Viscosity Dimensional Analysis",
    "question": "The volume flow rate Q (m\u00b3/s) \u221d \u03b7^a \u00d7 d^b \u00d7 (dP/dx)^c. Find the values of a, b, and c:",
    "options": {
      "a": "(\u22121, 4, 1)",
      "b": "(1, 1, 1)",
      "c": "(1, \u00bd, \u22121)",
      "d": "(2, 2, 1)"
    },
    "answer": "a",
    "explanation": "From Poiseuille's law Q = \u03c0r\u2074/(8\u03b7) \u00d7 (\u0394P/L), dimensional analysis gives Q \u221d \u03b7\u207b\u00b9 \u00d7 d\u2074 \u00d7 (dP/dx)\u00b9, so (a, b, c) = (\u22121, 4, 1)."
  },
  {
    "id": 99,
    "topic": "Surface Tension",
    "question": "Capillary rise explains which phenomena?",
    "options": {
      "a": "The flow of blood in veins",
      "b": "The movement of water in porous paper",
      "c": "The absorption of water by roots",
      "d": "All of the above"
    },
    "answer": "d",
    "explanation": "Capillary action explains water movement in narrow tubes/pores \u2014 it applies to blood flow in capillaries, chromatography paper, and water absorption in plant roots."
  },
  {
    "id": 100,
    "topic": "Surface Tension \u2013 Soap for Washing",
    "question": "Washing soap is used for cleaning clothes because:",
    "options": {
      "a": "It absorbs dirt",
      "b": "It increases the surface tension of the solution",
      "c": "It reduces the surface tension of the solution",
      "d": "It increases the viscosity of the liquid"
    },
    "answer": "c",
    "explanation": "Soap reduces surface tension, allowing water to spread better over fabric surfaces and penetrate into fibres, loosening dirt."
  },
  {
    "id": 101,
    "topic": "Fluid Mechanics \u2013 Viscous Force",
    "question": "What is the viscous force in a liquid of viscosity 0.5 Pa\u00b7s which covers an area of 0.4 m\u00b2 with a velocity gradient of 200/s?",
    "options": {
      "a": "20 N",
      "b": "60 N",
      "c": "80 N",
      "d": "40 N"
    },
    "answer": "d",
    "explanation": "Newton's law of viscosity: F = \u03b7 \u00d7 A \u00d7 (dv/dx) = 0.5 \u00d7 0.4 \u00d7 200 = 40 N"
  },
  {
    "id": 102,
    "topic": "Thermometry \u2013 Non-standard Scale",
    "question": "A thermometer reads 20\u00b0C in ice water and 100\u00b0C in boiling water. What is the Fahrenheit value at 60\u00b0C?",
    "options": {
      "a": "120\u00b0F",
      "b": "132\u00b0F",
      "c": "140\u00b0F",
      "d": "150\u00b0F"
    },
    "answer": "c",
    "explanation": "The thermometer's range: 20\u00b0C to 100\u00b0C = 80 divisions. 60\u00b0C is 40 units above ice point. Fraction = 40/80 = 0.5. On Fahrenheit scale: F = 32 + 0.5 \u00d7 180 = 32 + 90 = ... but the selected answer is 140\u00b0F. Using the non-standard scale: fraction of scale = (60-20)/(100-20) = 0.5; mapping to F = 32 + 0.5\u00d7(212-32) = 32+90 = 122\u00b0F. The course selects c = 140\u00b0F \u2014 verify with your lecturer's notes."
  },
  {
    "id": 103,
    "topic": "Fluid Mechanics \u2013 Hydrostatic Pressure",
    "question": "The pressure at a certain depth in a liquid column is given by:",
    "options": {
      "a": "P = h\u03c1g",
      "b": "P = h(\u03c1/g)",
      "c": "P = g/(h\u03c1)",
      "d": "P = hg"
    },
    "answer": "a",
    "explanation": "Hydrostatic pressure: P = h\u03c1g, where h = depth, \u03c1 = density of liquid, g = gravitational acceleration."
  },
  {
    "id": 104,
    "topic": "Thermal Expansion \u2013 Gases vs Liquids",
    "question": "Which statement is correct about the thermal expansion of gases?",
    "options": {
      "a": "Gases expand more at a given temperature than liquids",
      "b": "When temperature increases, the volume of gas decreases",
      "c": "When pressure increases, the volume increases",
      "d": "The main factors that determine the thermal expansion of gases are mass and density"
    },
    "answer": "a",
    "explanation": "Gases have much larger coefficients of thermal expansion than liquids or solids because their molecules are far apart and held by weaker intermolecular forces."
  },
  {
    "id": 105,
    "topic": "Thermodynamics \u2013 Heat Engine",
    "question": "The efficiency of a heat engine is 25%. If it absorbs 800 J of heat, how much work does it perform?",
    "options": {
      "a": "100 J",
      "b": "200 J",
      "c": "300 J",
      "d": "400 J"
    },
    "answer": "b",
    "explanation": "W = \u03b7 \u00d7 Q_H = 0.25 \u00d7 800 = 200 J"
  },
  {
    "id": 106,
    "topic": "Fluid Mechanics \u2013 Pascal's Law",
    "question": "A hydraulic press works on the principle of:",
    "options": {
      "a": "Archimedes' principle",
      "b": "Bernoulli's theorem",
      "c": "Pascal's law",
      "d": "Newton's second law"
    },
    "answer": "c",
    "explanation": "Pascal's law states that pressure applied to an enclosed fluid is transmitted equally in all directions \u2014 the operating principle of hydraulic presses and lifts."
  },
  {
    "id": 107,
    "topic": "Thermometry \u2013 Resistance Thermometer (Adebayo scale)",
    "question": "At the temperature scale of Adebayo's thermometer, the resistance values were 5 \u03a9 and 75 \u03a9 at the cool and hot extremes respectively. If an object measures 60 \u03a9, what is the corresponding temperature in Kelvin?",
    "options": {
      "a": "320.3 K",
      "b": "335.5 K",
      "c": "351.6 K",
      "d": "373.1 K"
    },
    "answer": "c",
    "explanation": "Fraction of scale: (60\u22125)/(75\u22125) = 55/70 = 0.7857. Mapping to Celsius (0\u00b0C to 100\u00b0C): T_C = 0.7857 \u00d7 100 = 78.57\u00b0C. In Kelvin: T_K = 78.57 + 273.15 \u2248 351.7 K \u2248 351.6 K."
  },
  {
    "id": 108,
    "topic": "Fluid Mechanics \u2013 Boyle's Law / Sealed Tube",
    "question": "An open glass tube is immersed in mercury so that 8 cm extends above the mercury level. The tube is sealed and raised vertically by 46 cm. (Atmospheric pressure = 76 cm of Hg). The length of the air column now is:",
    "options": {
      "a": "6 cm",
      "b": "22 cm",
      "c": "38 cm",
      "d": "16 cm"
    },
    "answer": "d",
    "explanation": "Initial: L\u2081 = 8 cm, P\u2081 = 76 cmHg. After raising 46 cm: tube top is 54 cm above original mercury, new air column length = L\u2082. New pressure P\u2082 = 76 \u2212 (54 \u2212 L\u2082) cmHg. By Boyle's law: P\u2081L\u2081 = P\u2082L\u2082 \u2192 76\u00d78 = (76\u221254+L\u2082)\u00d7L\u2082 \u2192 608 = (22+L\u2082)L\u2082. Solving: L\u2082\u00b2 + 22L\u2082 \u2212 608 = 0 \u2192 L\u2082 = (\u221222 + \u221a(484+2432))/2 = (\u221222+54)/2 = 16 cm."
  },
  {
    "id": 109,
    "topic": "Thermodynamics \u2013 Latent Heat Calculation",
    "question": "Calculate the heat energy lost when 10 g of boiling water changes to ice at 0\u00b0C. (Specific Latent Heat of ice = 336 J/g; specific heat capacity of water = 4.2 J/g\u00b7K)",
    "options": {
      "a": "4200 J",
      "b": "3360 J",
      "c": "10800 J",
      "d": "7560 J"
    },
    "answer": "d",
    "explanation": "Heat lost = cooling from 100\u00b0C to 0\u00b0C + latent heat of freezing. Q = mc\u0394T + mL = 10\u00d74.2\u00d7100 + 10\u00d7336 = 4200 + 3360 = 7560 J."
  },
  {
    "id": 110,
    "topic": "Fluid Mechanics \u2013 Bernoulli's Equation",
    "question": "A pipe used in a Bernoulli experiment has a change in potential energy per unit volume of 50 J/m\u00b3 and kinetic energy per unit volume of 40 J/m\u00b3. Calculate the change in pressure (in J/m\u00b3):",
    "options": {
      "a": "10",
      "b": "0.8",
      "c": "90",
      "d": "1.25"
    },
    "answer": "c",
    "explanation": "By Bernoulli's theorem: \u0394P + \u0394KE/vol + \u0394PE/vol = 0 \u2192 \u0394P = \u2212(40 + 50) = \u221290 J/m\u00b3. The magnitude of the pressure change is 90 J/m\u00b3."
  },
  {
    "id": 111,
    "topic": "Elasticity \u2013 Young's Modulus Unit",
    "question": "Which of the following is the correct unit of Young's modulus?",
    "options": {
      "a": "Pascal (Pa)",
      "b": "Newton (N)",
      "c": "Joule (J)",
      "d": "Watt (W)"
    },
    "answer": "a",
    "explanation": "Young's modulus = Stress/Strain = (N/m\u00b2)/dimensionless = Pa (Pascal). Note: The course-selected answer may differ \u2014 verify with your lecturer."
  },
  {
    "id": 112,
    "topic": "Thermodynamics \u2013 Triple Point",
    "question": "The temperature and pressure at which the solid, liquid, and vapour phases of a pure substance can coexist in equilibrium is called its ________ point.",
    "options": {
      "a": "Anomalous",
      "b": "Regelation",
      "c": "Balancing",
      "d": "Triple"
    },
    "answer": "d",
    "explanation": "The triple point is the unique temperature and pressure at which all three phases of a substance coexist in thermodynamic equilibrium."
  },
  {
    "id": 113,
    "topic": "Kinetic Theory \u2013 KE and Pressure",
    "question": "The pressure of an ideal gas is increased by keeping temperature constant. The kinetic energy of the molecules:",
    "options": {
      "a": "Decreases",
      "b": "Increases",
      "c": "Remains the same",
      "d": "Increases or decreases depending on the nature of gas"
    },
    "answer": "c",
    "explanation": "For an ideal gas, KE_avg = (3/2)kT \u2014 it depends only on temperature, not pressure. At constant temperature, KE remains unchanged."
  },
  {
    "id": 114,
    "topic": "Fluid Mechanics \u2013 Coefficient of Viscosity (Stokes)",
    "question": "A metal sphere of diameter 10 mm is dropped into glycerin. Viscous force = 2.5 N; Terminal velocity = 6 m/s. The coefficient of viscosity \u03b7 is:",
    "options": {
      "a": "3.01 Ns/m\u00b2",
      "b": "5.60 Ns/m\u00b2",
      "c": "4.42 Ns/m\u00b2",
      "d": "2.32 Ns/m\u00b2"
    },
    "answer": "c",
    "explanation": "Stokes' law: F = 6\u03c0\u03b7rv. r = 5\u00d710\u207b\u00b3 m, v = 6 m/s, F = 2.5 N. \u03b7 = F/(6\u03c0rv) = 2.5/(6\u03c0\u00d70.005\u00d76) = 2.5/(0.5655) \u2248 4.42 Ns/m\u00b2."
  },
  {
    "id": 115,
    "topic": "Surface Tension \u2013 Soap Bubble Pressure",
    "question": "A soap bubble has diameter 4 mm. (Surface tension = 2.8 \u00d7 10\u207b\u00b2 N/m; Atmospheric pressure = 1 \u00d7 10\u2075 N/m\u00b2). Pressure inside the bubble is:",
    "options": {
      "a": "5.0026 \u00d7 10\u2075 N/m\u00b2",
      "b": "5.0026 \u00d7 10\u2074 N/m\u00b2",
      "c": "1.0056 \u00d7 10\u2075 N/m\u00b2",
      "d": "1.0056 \u00d7 10\u00b2 N/m\u00b2"
    },
    "answer": "c",
    "explanation": "Excess pressure in soap bubble: \u0394P = 4\u03c3/r = 4\u00d72.8\u00d710\u207b\u00b2/0.002 = 56 Pa. P_inside = 10\u2075 + 56 = 1.00056\u00d710\u2075 \u2248 1.0056\u00d710\u2075 N/m\u00b2."
  },
  {
    "id": 116,
    "topic": "Surface Tension \u2013 Drop Merging",
    "question": "Two drops of a liquid are merged to form a single drop. In this process:",
    "options": {
      "a": "Energy is absorbed",
      "b": "Energy is released",
      "c": "Energy remains constant",
      "d": "Energy becomes half"
    },
    "answer": "b",
    "explanation": "When two drops merge, the total surface area decreases (volume conserved, but surface area of one large drop < two small drops). Since surface energy = T \u00d7 Area, a decrease in area means surface energy is released."
  },
  {
    "id": 117,
    "topic": "Thermodynamics \u2013 Ideal Gas Law",
    "question": "One mole of an ideal gas at 300 K occupies 0.024 m\u00b3. Using R = 8.31 J/mol\u00b7K, calculate its pressure.",
    "options": {
      "a": "8.31 \u00d7 10\u2075 Pa",
      "b": "1.04 \u00d7 10\u2075 Pa",
      "c": "2.49 \u00d7 10\u2075 Pa",
      "d": "3.12 \u00d7 10\u2075 Pa"
    },
    "answer": "b",
    "explanation": "PV = nRT \u2192 P = nRT/V = (1 \u00d7 8.31 \u00d7 300)/0.024 = 2493/0.024 \u2248 103,875 Pa \u2248 1.04 \u00d7 10\u2075 Pa."
  },
  {
    "id": 118,
    "topic": "Elasticity \u2013 Bulk Modulus and Poisson's Ratio",
    "question": "The Young's modulus of elasticity of a material is 150 GPa and Poisson's ratio is 0.5. Find the bulk modulus:",
    "options": {
      "a": "Zero",
      "b": "Infinity",
      "c": "0.5",
      "d": "1"
    },
    "answer": "b",
    "explanation": "Bulk modulus K = Y / [3(1 \u2212 2\u03bd)] = 150 / [3(1 \u2212 2\u00d70.5)] = 150/(3\u00d70) \u2192 infinity. A Poisson's ratio of 0.5 means the material is incompressible (like rubber), giving infinite bulk modulus."
  },
  {
    "id": 119,
    "topic": "Fluid Mechanics \u2013 Momentum Force",
    "question": "A water jet exits a nozzle at 10 m/s and strikes a stationary wall normally. The mass flow rate is 0.05 kg/s. What is the force exerted on the wall?",
    "options": {
      "a": "0.5 N",
      "b": "0.75 N",
      "c": "1.0 N",
      "d": "1.5 N"
    },
    "answer": "a",
    "explanation": "Force = rate of change of momentum = \u1e41 \u00d7 \u0394v = 0.05 \u00d7 10 = 0.5 N."
  },
  {
    "id": 120,
    "topic": "Thermometry \u2013 Celsius to Fahrenheit",
    "question": "37\u00b0C is equal to how many degrees Fahrenheit?",
    "options": {
      "a": "98.0\u00b0F",
      "b": "97.6\u00b0F",
      "c": "96.8\u00b0F",
      "d": "98.6\u00b0F"
    },
    "answer": "d",
    "explanation": "F = (9/5)C + 32 = (9/5\u00d737) + 32 = 66.6 + 32 = 98.6\u00b0F. Note: The course may accept a = 98.0\u00b0F as an approximation \u2014 verify with your lecturer."
  },
  {
    "id": 121,
    "topic": "Fluid Mechanics \u2013 Pump Power",
    "question": "Water flows at 0.2 m\u00b3/s from a point 15 m above ground. (\u03c1 = 1000 kg/m\u00b3, g = 10 m/s\u00b2). Calculate the power that drives the water:",
    "options": {
      "a": "1000 W",
      "b": "5000 W",
      "c": "10000 W",
      "d": "20000 W"
    },
    "answer": "d",
    "explanation": "P = \u03c1gQh = 1000\u00d710\u00d70.2\u00d715 = 30,000 W. The course-selected answer is 20,000 W (corresponding to h=10 m). The exact value depends on the height used \u2014 verify with your lecturer."
  },
  {
    "id": 122,
    "topic": "Thermometry \u2013 Celsius to Fahrenheit",
    "question": "If the temperature of a patient is 40\u00b0C, what will be his temperature on the Fahrenheit scale?",
    "options": {
      "a": "98\u00b0F",
      "b": "108\u00b0F",
      "c": "104\u00b0F",
      "d": "106\u00b0F"
    },
    "answer": "c",
    "explanation": "F = (9/5)C + 32 = (9/5\u00d740) + 32 = 72 + 32 = 104\u00b0F."
  },
  {
    "id": 123,
    "topic": "Thermodynamics \u2013 Absolute Zero",
    "question": "At which temperature does the volume of a gas reduce to zero?",
    "options": {
      "a": "273 K",
      "b": "0\u00b0C",
      "c": "273\u00b0C",
      "d": "0 K"
    },
    "answer": "d",
    "explanation": "According to Charles's Law extrapolated to ideal gases, volume \u2192 0 at absolute zero, i.e., 0 K (= \u2212273\u00b0C)."
  },
  {
    "id": 124,
    "topic": "Thermodynamics \u2013 Ideal Gas Law (Container)",
    "question": "A 1.0 m\u00b3 container holds 2 moles of ideal gas at 300 K. Calculate the pressure. (R = 8.31 J/mol\u00b7K)",
    "options": {
      "a": "2.49 \u00d7 10\u00b3 Pa",
      "b": "4.98 \u00d7 10\u00b3 Pa",
      "c": "4.98 \u00d7 10\u2074 Pa",
      "d": "2.49 \u00d7 10\u2075 Pa"
    },
    "answer": "b",
    "explanation": "PV = nRT \u2192 P = nRT/V = (2 \u00d7 8.31 \u00d7 300)/1 = 4986 Pa \u2248 4.98 \u00d7 10\u00b3 Pa."
  },
  {
    "id": 125,
    "topic": "Elasticity \u2013 SHM Maximum Acceleration",
    "question": "A force of 140 N stretches a horizontal spring by 0.25 m with a 0.7 kg block attached. Spring constant = 1200 N/m. If the system performs SHM, the maximum acceleration is:",
    "options": {
      "a": "600 m/s\u00b2",
      "b": "360,000 m/s\u00b2",
      "c": "200 m/s\u00b2",
      "d": "0.125 m/s\u00b2"
    },
    "answer": "c",
    "explanation": "Course method: a_max = F/m = 140/0.7 = 200 m/s\u00b2. (Note: The standard SHM formula a_max = kA/m = 1200\u00d70.25/0.7 \u2248 428 m/s\u00b2, but the course uses F/m directly.)"
  },
  {
    "id": 126,
    "topic": "Thermometry \u2013 Resistance Thermometer",
    "question": "In a resistance thermometer, the resistance at 0\u00b0C and 100\u00b0C are 5.8 \u03a9 and 8.4 \u03a9 respectively. The temperature corresponding to 6.2 \u03a9 resistance is:",
    "options": {
      "a": "12.40\u00b0C",
      "b": "13.40\u00b0C",
      "c": "15.40\u00b0C",
      "d": "14.40\u00b0C"
    },
    "answer": "c",
    "explanation": "T = (R \u2212 R\u2080)/(R\u2081\u2080\u2080 \u2212 R\u2080) \u00d7 100 = (6.2 \u2212 5.8)/(8.4 \u2212 5.8) \u00d7 100 = 0.4/2.6 \u00d7 100 \u2248 15.38\u00b0C \u2248 15.40\u00b0C."
  },
  {
    "id": 127,
    "topic": "Thermometry \u2013 Platinum Resistance Thermometer",
    "question": "A platinum-resistance thermometer has a resistance of 4 \u03a9 at 0\u00b0C and 12 \u03a9 at 100\u00b0C. Calculate the resistance when the temperature is 45\u00b0C:",
    "options": {
      "a": "6.4 \u03a9",
      "b": "7.6 \u03a9",
      "c": "8.2 \u03a9",
      "d": "9.4 \u03a9"
    },
    "answer": "b",
    "explanation": "Assuming linear variation: R = R\u2080 + (R\u2081\u2080\u2080 \u2212 R\u2080) \u00d7 T/100 = 4 + (12 \u2212 4) \u00d7 45/100 = 4 + 8\u00d70.45 = 4 + 3.6 = 7.6 \u03a9."
  },
  {
    "id": 128,
    "topic": "Elasticity \u2013 Bulk Modulus",
    "question": "Bulk modulus is related to what?",
    "options": {
      "a": "Change in length",
      "b": "Change in shape",
      "c": "Change in volume",
      "d": "Change in mass"
    },
    "answer": "c",
    "explanation": "Bulk modulus K = \u2212V(dP/dV) describes a material's resistance to uniform compression \u2014 it relates to change in volume."
  },
  {
    "id": 129,
    "topic": "Thermodynamics \u2013 Phase Change",
    "question": "On heating, a solid is directly converted into a gaseous state. This process is:",
    "options": {
      "a": "Evaporation",
      "b": "Sublimation",
      "c": "Diffusion",
      "d": "Condensation"
    },
    "answer": "b",
    "explanation": "Sublimation is the direct phase transition from solid to gas without passing through the liquid state, e.g., dry ice (CO\u2082) or iodine crystals."
  },
  {
    "id": 130,
    "topic": "Fluid Mechanics \u2013 Terminal Velocity",
    "question": "After terminal velocity is reached, the acceleration of a falling body in a fluid is:",
    "options": {
      "a": "Zero",
      "b": "Equal to g",
      "c": "Less than g",
      "d": "Greater than g"
    },
    "answer": "a",
    "explanation": "At terminal velocity, the net force is zero (weight = buoyancy + drag), so acceleration = 0."
  },
  {
    "id": 131,
    "topic": "Thermodynamics \u2013 Heat during Phase Change",
    "question": "The heat given to a substance during a phase change is:",
    "options": {
      "a": "Latent heat",
      "b": "Thermal capacity",
      "c": "None of the above",
      "d": "Specific heat"
    },
    "answer": "a",
    "explanation": "Latent heat is the energy absorbed or released during a phase change (e.g., melting, boiling) at constant temperature."
  },
  {
    "id": 132,
    "topic": "Thermodynamics \u2013 Gay-Lussac's Law (Constant Volume)",
    "question": "A 0.10 m\u00b3 tank contains gas at 2.0 \u00d7 10\u2075 Pa. If the temperature doubles at constant volume, what is the final pressure?",
    "options": {
      "a": "2.0 \u00d7 10\u2075 Pa",
      "b": "3.0 \u00d7 10\u2075 Pa",
      "c": "4.0 \u00d7 10\u2075 Pa",
      "d": "6.0 \u00d7 10\u2075 Pa"
    },
    "answer": "c",
    "explanation": "Gay-Lussac's Law: P/T = constant. If T doubles, P doubles: P\u2082 = 2 \u00d7 2.0\u00d710\u2075 = 4.0 \u00d7 10\u2075 Pa."
  },
  {
    "id": 133,
    "topic": "Thermometry \u2013 Kelvin equals Fahrenheit",
    "question": "A Kelvin thermometer and a Fahrenheit thermometer both give the same reading for a certain sample. The corresponding Celsius temperature is:",
    "options": {
      "a": "2320\u00b0C",
      "b": "6140\u00b0C",
      "c": "3010\u00b0C",
      "d": "5740\u00b0C"
    },
    "answer": "a",
    "explanation": "Setting K = F numerically: T_K = (9/5)(T_K \u2212 273.15) + 32 \u2192 solving: T_K \u2248 574.6 K \u2192 T_C = 574.6 \u2212 273.15 \u2248 301.4\u00b0C. The course selects a = 2320\u00b0C \u2014 verify this with your lecturer as the standard physics result is ~301\u00b0C."
  },
  {
    "id": 134,
    "topic": "Thermodynamics – Carnot Cycle",
    "question": "A Carnot engine operates between 500 K and 300 K. Its maximum possible efficiency is:",
    "options": {
      "a": "30%",
      "b": "40%",
      "c": "50%",
      "d": "60%"
    },
    "answer": "b",
    "explanation": "η_Carnot = 1 − T_C/T_H = 1 − 300/500 = 1 − 0.6 = 0.4 = 40%"
  },
  {
    "id": 135,
    "topic": "Thermodynamics – Entropy",
    "question": "In a reversible isothermal expansion, the entropy of the system:",
    "options": {
      "a": "Decreases",
      "b": "Remains constant",
      "c": "Increases",
      "d": "Becomes zero"
    },
    "answer": "c",
    "explanation": "During isothermal expansion, heat Q is absorbed from the reservoir. ΔS = Q/T > 0, so entropy increases."
  },
  {
    "id": 136,
    "topic": "Thermodynamics – Second Law",
    "question": "Which statement correctly expresses the Second Law of Thermodynamics?",
    "options": {
      "a": "Energy is conserved in all processes",
      "b": "Heat flows spontaneously from cold to hot",
      "c": "No engine can convert heat entirely to work",
      "d": "Entropy of the universe remains constant"
    },
    "answer": "c",
    "explanation": "The Kelvin-Planck statement: it is impossible to construct a heat engine that operates in a cycle and produces no effect other than the absorption of heat and the performance of an equivalent amount of work."
  },
  {
    "id": 137,
    "topic": "Thermodynamics – Specific Heat",
    "question": "How much heat is required to raise the temperature of 2 kg of water from 20°C to 70°C? (Specific heat of water = 4200 J/kg·K)",
    "options": {
      "a": "210 kJ",
      "b": "420 kJ",
      "c": "840 kJ",
      "d": "168 kJ"
    },
    "answer": "b",
    "explanation": "Q = mcΔT = 2 × 4200 × (70 − 20) = 2 × 4200 × 50 = 420,000 J = 420 kJ"
  },
  {
    "id": 138,
    "topic": "Thermodynamics – Ideal Gas",
    "question": "An ideal gas occupies 4 L at 300 K and 2 atm. What volume will it occupy at 600 K and 1 atm?",
    "options": {
      "a": "8 L",
      "b": "16 L",
      "c": "4 L",
      "d": "2 L"
    },
    "answer": "b",
    "explanation": "Using the combined gas law: P₁V₁/T₁ = P₂V₂/T₂ → V₂ = P₁V₁T₂/(T₁P₂) = (2 × 4 × 600)/(300 × 1) = 16 L"
  },
  {
    "id": 139,
    "topic": "Thermodynamics – Adiabatic Process",
    "question": "In an adiabatic process:",
    "options": {
      "a": "Temperature remains constant",
      "b": "Pressure remains constant",
      "c": "No heat exchange occurs",
      "d": "Volume remains constant"
    },
    "answer": "c",
    "explanation": "An adiabatic process is one in which no heat is exchanged between the system and its surroundings (Q = 0). From the First Law: ΔU = −W."
  },
  {
    "id": 140,
    "topic": "Thermodynamics – Latent Heat",
    "question": "How much energy is required to convert 500 g of ice at 0°C to water at 0°C? (Latent heat of fusion = 336 J/g)",
    "options": {
      "a": "168 J",
      "b": "168 kJ",
      "c": "336 kJ",
      "d": "672 kJ"
    },
    "answer": "b",
    "explanation": "Q = mL = 500 × 336 = 168,000 J = 168 kJ. No temperature change occurs during phase transition."
  },
  {
    "id": 141,
    "topic": "Thermodynamics – Isochoric Process",
    "question": "In an isochoric (constant volume) process, the work done by the gas is:",
    "options": {
      "a": "Maximum",
      "b": "Equal to heat added",
      "c": "Zero",
      "d": "Equal to internal energy change"
    },
    "answer": "c",
    "explanation": "W = PΔV = 0 at constant volume. All heat added goes into changing the internal energy: Q = ΔU."
  },
  {
    "id": 142,
    "topic": "Thermodynamics – Isothermal Process",
    "question": "In an isothermal process for an ideal gas:",
    "options": {
      "a": "Internal energy changes",
      "b": "PV = constant",
      "c": "Q = 0",
      "d": "V/T = constant"
    },
    "answer": "b",
    "explanation": "For an isothermal process (T = constant), the ideal gas law gives PV = nRT = constant. Hence PV = constant (Boyle's Law)."
  },
  {
    "id": 143,
    "topic": "Thermodynamics – Heat Engine",
    "question": "A heat engine takes in 800 J per cycle and does 200 J of work. The efficiency is:",
    "options": {
      "a": "12.5%",
      "b": "25%",
      "c": "40%",
      "d": "75%"
    },
    "answer": "b",
    "explanation": "η = W/Q_H = 200/800 = 0.25 = 25%"
  },
  {
    "id": 144,
    "topic": "Fluid Mechanics – Bernoulli's Theorem",
    "question": "Bernoulli's equation is an expression of:",
    "options": {
      "a": "Conservation of mass",
      "b": "Conservation of momentum",
      "c": "Conservation of energy",
      "d": "Newton's third law"
    },
    "answer": "c",
    "explanation": "Bernoulli's equation (P + ½ρv² + ρgh = constant) is derived from the conservation of energy applied to fluid flow."
  },
  {
    "id": 145,
    "topic": "Fluid Mechanics – Continuity Equation",
    "question": "Water flows through a pipe of cross-section 4 cm² at 3 m/s. If the pipe narrows to 2 cm², the new speed is:",
    "options": {
      "a": "1.5 m/s",
      "b": "3 m/s",
      "c": "6 m/s",
      "d": "12 m/s"
    },
    "answer": "c",
    "explanation": "By continuity: A₁v₁ = A₂v₂ → v₂ = A₁v₁/A₂ = (4 × 3)/2 = 6 m/s"
  },
  {
    "id": 146,
    "topic": "Fluid Mechanics – Viscosity",
    "question": "The SI unit of dynamic viscosity is:",
    "options": {
      "a": "Pa",
      "b": "Pa·s",
      "c": "N/m²",
      "d": "kg/m³"
    },
    "answer": "b",
    "explanation": "Dynamic viscosity η is defined from τ = η(dv/dy). Its SI unit is Pascal-second (Pa·s), also written N·s/m²."
  },
  {
    "id": 147,
    "topic": "Fluid Mechanics – Stokes' Law",
    "question": "A sphere of radius r falls through a viscous fluid with terminal velocity v. The viscous drag force is given by:",
    "options": {
      "a": "F = 2πηrv",
      "b": "F = 4πηrv",
      "c": "F = 6πηrv",
      "d": "F = πηrv"
    },
    "answer": "c",
    "explanation": "Stokes' Law: F = 6πηrv, where η is dynamic viscosity, r is sphere radius, and v is the velocity."
  },
  {
    "id": 148,
    "topic": "Fluid Mechanics – Terminal Velocity",
    "question": "At terminal velocity, the net force on a falling body is:",
    "options": {
      "a": "Maximum downward",
      "b": "Equal to weight",
      "c": "Zero",
      "d": "Equal to buoyant force"
    },
    "answer": "c",
    "explanation": "At terminal velocity, weight = drag force + buoyant force, so the net force is zero and acceleration is zero."
  },
  {
    "id": 149,
    "topic": "Fluid Mechanics – Pressure",
    "question": "The pressure at a depth h in a liquid of density ρ is given by:",
    "options": {
      "a": "P = ρg/h",
      "b": "P = ρgh",
      "c": "P = ρh/g",
      "d": "P = g/ρh"
    },
    "answer": "b",
    "explanation": "Hydrostatic pressure: P = ρgh, where ρ is fluid density, g is gravitational acceleration, and h is depth."
  },
  {
    "id": 150,
    "topic": "Fluid Mechanics – Archimedes' Principle",
    "question": "A wooden block displaces 500 cm³ of water when floating. The buoyant force is: (ρ_water = 1000 kg/m³, g = 10 m/s²)",
    "options": {
      "a": "0.5 N",
      "b": "5 N",
      "c": "50 N",
      "d": "500 N"
    },
    "answer": "b",
    "explanation": "F_B = ρVg = 1000 × 500×10⁻⁶ × 10 = 1000 × 5×10⁻⁴ × 10 = 5 N"
  },
  {
    "id": 151,
    "topic": "Fluid Mechanics – Laminar vs Turbulent",
    "question": "Flow becomes turbulent when the Reynolds number exceeds approximately:",
    "options": {
      "a": "100",
      "b": "500",
      "c": "2000",
      "d": "10000"
    },
    "answer": "c",
    "explanation": "For flow in a pipe, laminar flow exists for Re < ~2000. Above ~4000 flow is turbulent. Between 2000–4000 is a transitional regime."
  },
  {
    "id": 152,
    "topic": "Fluid Mechanics – Reynolds Number",
    "question": "Reynolds number is a ratio of:",
    "options": {
      "a": "Pressure force to viscous force",
      "b": "Inertial force to viscous force",
      "c": "Buoyant force to gravitational force",
      "d": "Surface tension to inertial force"
    },
    "answer": "b",
    "explanation": "Re = ρvL/η represents the ratio of inertial forces to viscous forces in a fluid. Higher Re means inertia dominates and flow tends to turbulence."
  },
  {
    "id": 153,
    "topic": "Fluid Mechanics – Gauge Pressure",
    "question": "Gauge pressure is:",
    "options": {
      "a": "Absolute pressure + atmospheric pressure",
      "b": "Absolute pressure − atmospheric pressure",
      "c": "Atmospheric pressure − absolute pressure",
      "d": "Equal to absolute pressure"
    },
    "answer": "b",
    "explanation": "Gauge pressure = Absolute pressure − Atmospheric pressure. It is the pressure measured relative to atmospheric pressure."
  },
  {
    "id": 154,
    "topic": "Fluid Mechanics – Torricelli",
    "question": "Water leaks from a small hole at the base of a tank filled to height h = 5 m. The exit speed is: (g = 10 m/s²)",
    "options": {
      "a": "5 m/s",
      "b": "7.07 m/s",
      "c": "10 m/s",
      "d": "50 m/s"
    },
    "answer": "c",
    "explanation": "By Torricelli's theorem: v = √(2gh) = √(2 × 10 × 5) = √100 = 10 m/s"
  },
  {
    "id": 155,
    "topic": "Elasticity – Young's Modulus",
    "question": "A wire of length 2 m and cross-sectional area 1×10⁻⁶ m² stretches by 0.002 m when a 100 N force is applied. Young's modulus is:",
    "options": {
      "a": "1×10⁸ Pa",
      "b": "1×10¹⁰ Pa",
      "c": "1×10¹¹ Pa",
      "d": "5×10⁹ Pa"
    },
    "answer": "b",
    "explanation": "Y = (F/A)/(ΔL/L) = (100/10⁻⁶)/(0.002/2) = 10⁸/10⁻³ = 10¹⁰ Pa"
  },
  {
    "id": 156,
    "topic": "Elasticity – Stress",
    "question": "A rod of cross-sectional area 0.01 m² supports a load of 5000 N. The stress in the rod is:",
    "options": {
      "a": "50 Pa",
      "b": "500 Pa",
      "c": "5×10⁵ Pa",
      "d": "5×10⁷ Pa"
    },
    "answer": "c",
    "explanation": "Stress = F/A = 5000/0.01 = 500,000 Pa = 5×10⁵ Pa"
  },
  {
    "id": 157,
    "topic": "Elasticity – Strain",
    "question": "A 1.5 m rod stretches by 3 mm under load. The longitudinal strain is:",
    "options": {
      "a": "0.001",
      "b": "0.002",
      "c": "0.003",
      "d": "0.0015"
    },
    "answer": "b",
    "explanation": "Strain = ΔL/L = 0.003/1.5 = 0.002"
  },
  {
    "id": 158,
    "topic": "Elasticity – Hooke's Law",
    "question": "Within the elastic limit, stress is:",
    "options": {
      "a": "Inversely proportional to strain",
      "b": "Directly proportional to strain",
      "c": "Equal to strain",
      "d": "Independent of strain"
    },
    "answer": "b",
    "explanation": "Hooke's Law states that stress is directly proportional to strain within the elastic limit: stress = E × strain, where E is the elastic modulus."
  },
  {
    "id": 159,
    "topic": "Elasticity – Bulk Modulus",
    "question": "Bulk modulus of elasticity relates:",
    "options": {
      "a": "Shear stress to shear strain",
      "b": "Tensile stress to tensile strain",
      "c": "Hydrostatic pressure to volumetric strain",
      "d": "Bending moment to curvature"
    },
    "answer": "c",
    "explanation": "Bulk modulus K = −ΔP/(ΔV/V). It relates the change in hydrostatic pressure to the resulting fractional change in volume."
  },
  {
    "id": 160,
    "topic": "Elasticity – Shear Modulus",
    "question": "Shear modulus (modulus of rigidity) G is defined as:",
    "options": {
      "a": "Normal stress/Normal strain",
      "b": "Shear stress/Shear strain",
      "c": "Hydrostatic stress/Volumetric strain",
      "d": "Lateral strain/Longitudinal strain"
    },
    "answer": "b",
    "explanation": "Shear modulus G = Shear stress/Shear strain = τ/γ. It measures resistance to shape change without volume change."
  },
  {
    "id": 161,
    "topic": "Elasticity – Poisson's Ratio",
    "question": "Poisson's ratio is defined as:",
    "options": {
      "a": "Longitudinal strain/Lateral strain",
      "b": "Lateral strain/Longitudinal strain",
      "c": "Shear strain/Normal strain",
      "d": "Volume strain/Linear strain"
    },
    "answer": "b",
    "explanation": "Poisson's ratio ν = −(lateral strain)/(longitudinal strain). It is always positive (material expands laterally when compressed longitudinally)."
  },
  {
    "id": 162,
    "topic": "Elasticity – Elastic Limit",
    "question": "Beyond the elastic limit, a material:",
    "options": {
      "a": "Returns to original shape",
      "b": "Undergoes permanent deformation",
      "c": "Breaks immediately",
      "d": "Becomes liquid"
    },
    "answer": "b",
    "explanation": "Beyond the elastic limit (yield point), plastic deformation occurs — the material does not return to its original shape upon removal of the load."
  },
  {
    "id": 163,
    "topic": "Elasticity – Energy in Deformation",
    "question": "The elastic potential energy stored per unit volume in a strained material is:",
    "options": {
      "a": "Stress × Strain",
      "b": "½ × Stress × Strain",
      "c": "Stress² / (2E)",
      "d": "Both b and c"
    },
    "answer": "d",
    "explanation": "Energy per unit volume = ½ × stress × strain = ½ × σ × ε = σ²/(2E) = Eε²/2. Options b and c are both equivalent correct expressions."
  },
  {
    "id": 164,
    "topic": "Surface Tension – Capillarity",
    "question": "Water rises in a capillary tube because:",
    "options": {
      "a": "Adhesion > Cohesion",
      "b": "Cohesion > Adhesion",
      "c": "Gravity pulls it up",
      "d": "Atmospheric pressure is zero inside"
    },
    "answer": "a",
    "explanation": "When adhesive forces (liquid–glass) exceed cohesive forces (liquid–liquid), the meniscus is concave and liquid rises. Mercury falls because cohesion > adhesion."
  },
  {
    "id": 165,
    "topic": "Surface Tension – Capillary Rise",
    "question": "A capillary tube of radius 0.5 mm is dipped in water. The height of rise is: (T = 0.072 N/m, ρ = 1000 kg/m³, g = 9.8 m/s², θ ≈ 0°)",
    "options": {
      "a": "1.47 cm",
      "b": "2.94 cm",
      "c": "0.74 cm",
      "d": "5.88 cm"
    },
    "answer": "b",
    "explanation": "h = 2T cosθ/(ρgr) = 2 × 0.072 × 1/(1000 × 9.8 × 0.0005) = 0.144/4.9 ≈ 0.0294 m = 2.94 cm"
  },
  {
    "id": 166,
    "topic": "Surface Tension – Pressure Inside Bubble",
    "question": "The excess pressure inside a soap bubble of radius R and surface tension T is:",
    "options": {
      "a": "T/R",
      "b": "2T/R",
      "c": "4T/R",
      "d": "T/(2R)"
    },
    "answer": "c",
    "explanation": "A soap bubble has two surfaces. Excess pressure = 4T/R. For a single liquid drop or air bubble in liquid, excess pressure = 2T/R."
  },
  {
    "id": 167,
    "topic": "Surface Tension – Pressure in Droplet",
    "question": "The excess pressure inside a liquid droplet of radius R is:",
    "options": {
      "a": "T/R",
      "b": "2T/R",
      "c": "4T/R",
      "d": "T/(4R)"
    },
    "answer": "b",
    "explanation": "A liquid droplet has only one free surface. Excess pressure ΔP = 2T/R."
  },
  {
    "id": 168,
    "topic": "Surface Tension – Angle of Contact",
    "question": "For mercury in a glass tube, the meniscus is convex because:",
    "options": {
      "a": "Mercury's cohesion < adhesion with glass",
      "b": "Mercury's cohesion > adhesion with glass",
      "c": "Mercury density is very high",
      "d": "Contact angle is less than 90°"
    },
    "answer": "b",
    "explanation": "Mercury has very strong cohesive forces (intermercury) that exceed adhesive forces (mercury-glass). This causes a convex meniscus and depression in capillary tubes."
  },
  {
    "id": 169,
    "topic": "Surface Tension – Work Done",
    "question": "The work done in blowing a soap bubble from radius r₁ to r₂ is:",
    "options": {
      "a": "4πT(r₂² − r₁²)",
      "b": "2πT(r₂² − r₁²)",
      "c": "8πT(r₂² − r₁²)",
      "d": "πT(r₂² − r₁²)"
    },
    "answer": "c",
    "explanation": "A soap bubble has 2 surfaces. Surface area = 2 × 4πr² = 8πr². Work = T × ΔA = T × 8π(r₂² − r₁²) = 8πT(r₂² − r₁²)"
  },
  {
    "id": 170,
    "topic": "Surface Tension – Effect of Temperature",
    "question": "As temperature increases, surface tension of a liquid:",
    "options": {
      "a": "Increases",
      "b": "Decreases",
      "c": "Remains unchanged",
      "d": "First increases then decreases"
    },
    "answer": "b",
    "explanation": "Higher temperature increases molecular kinetic energy and reduces intermolecular cohesive forces, thereby decreasing surface tension. Surface tension → 0 at critical temperature."
  },
  {
    "id": 171,
    "topic": "Waves – Simple Harmonic Motion",
    "question": "In simple harmonic motion, the restoring force is:",
    "options": {
      "a": "Constant in magnitude",
      "b": "Proportional to displacement and directed away from equilibrium",
      "c": "Proportional to displacement and directed toward equilibrium",
      "d": "Proportional to velocity"
    },
    "answer": "c",
    "explanation": "SHM is defined by F = −kx, where the restoring force is proportional to displacement x and always directed toward the equilibrium position (negative sign)."
  },
  {
    "id": 172,
    "topic": "Waves – Period of Simple Pendulum",
    "question": "A simple pendulum of length 0.25 m has a period of: (g = 10 m/s²)",
    "options": {
      "a": "π/10 s",
      "b": "π/5 s",
      "c": "π s",
      "d": "2π s"
    },
    "answer": "b",
    "explanation": "T = 2π√(L/g) = 2π√(0.25/10) = 2π√0.025 = 2π × 0.158 = π/5 ≈ 0.628 × 2 ≈ 3.14/5 s"
  },
  {
    "id": 173,
    "topic": "Waves – Wave Speed",
    "question": "A wave has frequency 200 Hz and wavelength 1.5 m. Its speed is:",
    "options": {
      "a": "133 m/s",
      "b": "300 m/s",
      "c": "201.5 m/s",
      "d": "198.5 m/s"
    },
    "answer": "b",
    "explanation": "v = fλ = 200 × 1.5 = 300 m/s"
  },
  {
    "id": 174,
    "topic": "Waves – Transverse vs Longitudinal",
    "question": "Sound waves in air are:",
    "options": {
      "a": "Transverse waves",
      "b": "Longitudinal waves",
      "c": "Electromagnetic waves",
      "d": "Torsional waves"
    },
    "answer": "b",
    "explanation": "Sound travels as longitudinal (compressional) waves — particles oscillate parallel to the direction of wave propagation through alternating compressions and rarefactions."
  },
  {
    "id": 175,
    "topic": "Waves – Superposition",
    "question": "When two waves of the same frequency and amplitude travel in opposite directions, they produce:",
    "options": {
      "a": "Beats",
      "b": "Diffraction",
      "c": "Standing waves",
      "d": "Doppler effect"
    },
    "answer": "c",
    "explanation": "Two waves of equal frequency and amplitude moving in opposite directions superpose to form standing (stationary) waves with fixed nodes and antinodes."
  },
  {
    "id": 176,
    "topic": "Waves – Beats",
    "question": "Two tuning forks have frequencies 440 Hz and 444 Hz. The beat frequency heard is:",
    "options": {
      "a": "884 Hz",
      "b": "2 Hz",
      "c": "4 Hz",
      "d": "440 Hz"
    },
    "answer": "c",
    "explanation": "Beat frequency = |f₁ − f₂| = |444 − 440| = 4 Hz. Beats are periodic variations in loudness due to interference of slightly different frequencies."
  },
  {
    "id": 177,
    "topic": "Waves – Resonance",
    "question": "Resonance occurs when the frequency of a driving force equals:",
    "options": {
      "a": "Twice the natural frequency",
      "b": "Half the natural frequency",
      "c": "The natural frequency of the system",
      "d": "Any frequency"
    },
    "answer": "c",
    "explanation": "Resonance occurs when the applied frequency matches the system's natural frequency. At resonance, energy transfer is maximum and amplitude is greatest."
  },
  {
    "id": 178,
    "topic": "Waves – Doppler Effect",
    "question": "A source of sound moves toward a stationary observer. The observed frequency is:",
    "options": {
      "a": "Lower than emitted frequency",
      "b": "Equal to emitted frequency",
      "c": "Higher than emitted frequency",
      "d": "Zero"
    },
    "answer": "c",
    "explanation": "When a source approaches an observer, sound wavefronts are compressed, reducing apparent wavelength and increasing observed frequency: f' = f(v/(v − v_s))."
  },
  {
    "id": 179,
    "topic": "Waves – Speed of Sound",
    "question": "The speed of sound in air at 0°C is approximately:",
    "options": {
      "a": "220 m/s",
      "b": "331 m/s",
      "c": "440 m/s",
      "d": "3×10⁸ m/s"
    },
    "answer": "b",
    "explanation": "The speed of sound in air at 0°C is approximately 331 m/s. It increases with temperature: v ≈ 331 + 0.6T m/s (T in °C)."
  },
  {
    "id": 180,
    "topic": "Waves – Fundamental Frequency",
    "question": "A string of length 0.6 m is fixed at both ends. The wavelength of the fundamental mode is:",
    "options": {
      "a": "0.3 m",
      "b": "0.6 m",
      "c": "1.2 m",
      "d": "2.4 m"
    },
    "answer": "c",
    "explanation": "For a string fixed at both ends: fundamental wavelength λ = 2L = 2 × 0.6 = 1.2 m. The fundamental has one antinode at the center."
  },
  {
    "id": 181,
    "topic": "Waves – Open Pipe",
    "question": "An open pipe of length L has a fundamental frequency of v/2L. What is its second harmonic frequency?",
    "options": {
      "a": "v/2L",
      "b": "v/L",
      "c": "3v/2L",
      "d": "2v/L"
    },
    "answer": "b",
    "explanation": "For an open pipe, harmonics are f_n = nv/2L. Second harmonic (n=2): f₂ = 2v/2L = v/L."
  },
  {
    "id": 182,
    "topic": "Waves – Closed Pipe",
    "question": "A closed pipe (closed at one end) supports only:",
    "options": {
      "a": "Even harmonics only",
      "b": "Odd harmonics only",
      "c": "All harmonics",
      "d": "No harmonics"
    },
    "answer": "b",
    "explanation": "A closed pipe has a node at the closed end and antinode at the open end. This allows only odd harmonics: f_n = nv/4L where n = 1, 3, 5, ..."
  },
  {
    "id": 183,
    "topic": "Heat Transfer – Conduction",
    "question": "Fourier's law of heat conduction states that heat flow rate is proportional to:",
    "options": {
      "a": "Temperature difference only",
      "b": "Area and temperature gradient",
      "c": "Length of conductor only",
      "d": "Density of the material"
    },
    "answer": "b",
    "explanation": "Q/t = −kA(dT/dx). Heat flow rate is proportional to thermal conductivity k, cross-sectional area A, and the temperature gradient dT/dx."
  },
  {
    "id": 184,
    "topic": "Heat Transfer – Radiation",
    "question": "Stefan-Boltzmann law states that the power radiated by a black body is proportional to:",
    "options": {
      "a": "T",
      "b": "T²",
      "c": "T³",
      "d": "T⁴"
    },
    "answer": "d",
    "explanation": "P = σAT⁴ (Stefan-Boltzmann law). Radiated power is proportional to the fourth power of absolute temperature T."
  },
  {
    "id": 185,
    "topic": "Heat Transfer – Newton's Law of Cooling",
    "question": "Newton's Law of Cooling states that the rate of heat loss is proportional to:",
    "options": {
      "a": "The absolute temperature of the body",
      "b": "The temperature difference between the body and surroundings",
      "c": "The square of temperature difference",
      "d": "The mass of the body"
    },
    "answer": "b",
    "explanation": "dQ/dt = −h·A·(T − T_s). The rate of heat loss is proportional to the temperature difference between the object and its surroundings."
  },
  {
    "id": 186,
    "topic": "Heat Transfer – Convection",
    "question": "In natural (free) convection, fluid motion is driven by:",
    "options": {
      "a": "Mechanical pumping",
      "b": "Density differences due to temperature variations",
      "c": "Pressure applied externally",
      "d": "Electromagnetic forces"
    },
    "answer": "b",
    "explanation": "In natural convection, warmer fluid becomes less dense and rises while cooler, denser fluid sinks. Gravity acting on these density differences drives circulation."
  },
  {
    "id": 187,
    "topic": "Heat Transfer – Thermal Conductivity",
    "question": "A good thermal conductor has:",
    "options": {
      "a": "Low thermal conductivity",
      "b": "High thermal conductivity",
      "c": "Zero thermal conductivity",
      "d": "Thermal conductivity independent of material"
    },
    "answer": "b",
    "explanation": "Thermal conductivity k measures how readily heat flows through a material. Metals like copper and silver have high k values and are good thermal conductors."
  },
  {
    "id": 188,
    "topic": "Thermodynamics – Carnot Efficiency",
    "question": "A Carnot engine operates between 627°C and 27°C. Its efficiency is:",
    "options": {
      "a": "50%",
      "b": "66.7%",
      "c": "75%",
      "d": "100%"
    },
    "answer": "b",
    "explanation": "T_H = 627 + 273 = 900 K, T_C = 27 + 273 = 300 K. η = 1 − T_C/T_H = 1 − 300/900 = 1 − 1/3 = 2/3 ≈ 66.7%"
  },
  {
    "id": 189,
    "topic": "Thermodynamics – Gas Laws",
    "question": "Charles' Law states that at constant pressure, volume is:",
    "options": {
      "a": "Inversely proportional to temperature",
      "b": "Directly proportional to absolute temperature",
      "c": "Independent of temperature",
      "d": "Proportional to the square of temperature"
    },
    "answer": "b",
    "explanation": "Charles' Law: V/T = constant (at constant pressure), or V₁/T₁ = V₂/T₂. T must be in Kelvin (absolute temperature)."
  },
  {
    "id": 190,
    "topic": "Thermodynamics – Gas Laws",
    "question": "Boyle's Law states that at constant temperature:",
    "options": {
      "a": "P ∝ V",
      "b": "PV = constant",
      "c": "P ∝ T",
      "d": "V ∝ T"
    },
    "answer": "b",
    "explanation": "Boyle's Law: PV = constant (at constant temperature). As pressure increases, volume decreases proportionally."
  },
  {
    "id": 191,
    "topic": "Thermodynamics – Avogadro's Law",
    "question": "Avogadro's Law states that equal volumes of gases at the same temperature and pressure contain:",
    "options": {
      "a": "Equal masses",
      "b": "Equal numbers of molecules",
      "c": "Equal kinetic energies per mole",
      "d": "Equal densities"
    },
    "answer": "b",
    "explanation": "Avogadro's Law: equal volumes of all gases at the same temperature and pressure contain equal numbers of molecules (or moles)."
  },
  {
    "id": 192,
    "topic": "Thermodynamics – Universal Gas Constant",
    "question": "The ideal gas equation PV = nRT involves the universal gas constant R, which equals approximately:",
    "options": {
      "a": "6.67 J/(mol·K)",
      "b": "8.314 J/(mol·K)",
      "c": "1.38×10⁻²³ J/K",
      "d": "96500 J/(mol·K)"
    },
    "answer": "b",
    "explanation": "R = 8.314 J/(mol·K) is the universal gas constant in PV = nRT. Note: k_B = 1.38×10⁻²³ J/K is the Boltzmann constant (per molecule)."
  },
  {
    "id": 193,
    "topic": "Thermodynamics – Entropy",
    "question": "The entropy of an isolated system always:",
    "options": {
      "a": "Decreases in spontaneous processes",
      "b": "Remains constant in all processes",
      "c": "Increases or stays constant (never decreases)",
      "d": "Decreases then increases"
    },
    "answer": "c",
    "explanation": "Second Law of Thermodynamics: the total entropy of an isolated system can only increase or remain constant in any spontaneous process (ΔS ≥ 0)."
  },
  {
    "id": 194,
    "topic": "Elasticity – Tensile Strength",
    "question": "Tensile strength is defined as the maximum:",
    "options": {
      "a": "Strain a material can undergo",
      "b": "Stress a material can withstand before fracture",
      "c": "Elastic modulus of the material",
      "d": "Elongation per unit length"
    },
    "answer": "b",
    "explanation": "Tensile strength (ultimate tensile strength) is the maximum stress a material can withstand while being stretched before fracturing."
  },
  {
    "id": 195,
    "topic": "Elasticity – Ductile vs Brittle",
    "question": "A brittle material:",
    "options": {
      "a": "Has a large plastic deformation region before fracture",
      "b": "Fractures with little or no plastic deformation",
      "c": "Cannot store elastic energy",
      "d": "Has infinite tensile strength"
    },
    "answer": "b",
    "explanation": "Brittle materials (e.g., glass, cast iron) fracture suddenly with little plastic deformation. Ductile materials (e.g., copper) show significant elongation before fracture."
  },
  {
    "id": 196,
    "topic": "Fluid Mechanics – Equation of Continuity",
    "question": "The equation of continuity in fluid dynamics expresses:",
    "options": {
      "a": "Conservation of energy",
      "b": "Conservation of momentum",
      "c": "Conservation of mass",
      "d": "Newton's second law"
    },
    "answer": "c",
    "explanation": "The continuity equation A₁v₁ = A₂v₂ (for incompressible flow) is a statement of conservation of mass: mass flow rate is constant."
  },
  {
    "id": 197,
    "topic": "Fluid Mechanics – Venturi Meter",
    "question": "A Venturi meter measures:",
    "options": {
      "a": "Viscosity of a fluid",
      "b": "Flow rate of a fluid in a pipe",
      "c": "Density of a fluid",
      "d": "Surface tension of a liquid"
    },
    "answer": "b",
    "explanation": "A Venturi meter uses the Bernoulli principle: by measuring the pressure difference between wide and narrow sections, the flow rate can be calculated."
  },
  {
    "id": 198,
    "topic": "Surface Tension – Wetting",
    "question": "A liquid is said to wet a surface when its contact angle is:",
    "options": {
      "a": "Greater than 90°",
      "b": "Equal to 180°",
      "c": "Less than 90°",
      "d": "Exactly 90°"
    },
    "answer": "c",
    "explanation": "Contact angle θ < 90° indicates a wetting liquid (e.g., water on glass). θ > 90° indicates non-wetting (e.g., mercury on glass)."
  },
  {
    "id": 199,
    "topic": "Thermodynamics – Refrigerator",
    "question": "The coefficient of performance (COP) of a refrigerator is defined as:",
    "options": {
      "a": "W/Q_H",
      "b": "Q_C/W",
      "c": "Q_H/W",
      "d": "W/Q_C"
    },
    "answer": "b",
    "explanation": "COP_refrigerator = Q_C/W, the heat removed from the cold reservoir divided by the work input. A higher COP means a more efficient refrigerator."
  },
  {
    "id": 200,
    "topic": "Thermodynamics – Heat Pump",
    "question": "The COP of a heat pump equals:",
    "options": {
      "a": "Q_C/W",
      "b": "W/Q_H",
      "c": "Q_H/W",
      "d": "Q_H/Q_C"
    },
    "answer": "c",
    "explanation": "COP_heat pump = Q_H/W. Note COP_HP = COP_refrigerator + 1, so a heat pump is always more efficient than an electric heater (COP > 1)."
  },
  {
    "id": 201,
    "topic": "Waves – Frequency and Period",
    "question": "A wave has a period of 0.02 s. Its frequency is:",
    "options": {
      "a": "20 Hz",
      "b": "50 Hz",
      "c": "0.02 Hz",
      "d": "2 Hz"
    },
    "answer": "b",
    "explanation": "f = 1/T = 1/0.02 = 50 Hz"
  },
  {
    "id": 202,
    "topic": "Waves – Amplitude and Energy",
    "question": "If the amplitude of a wave is doubled, the energy carried by the wave:",
    "options": {
      "a": "Doubles",
      "b": "Halves",
      "c": "Quadruples",
      "d": "Remains the same"
    },
    "answer": "c",
    "explanation": "Wave energy is proportional to the square of amplitude: E ∝ A². Doubling A gives E ∝ (2A)² = 4A², so energy quadruples."
  },
  {
    "id": 203,
    "topic": "Waves – Phase Difference",
    "question": "Two points on a wave are one full wavelength apart. Their phase difference is:",
    "options": {
      "a": "π/2 rad",
      "b": "π rad",
      "c": "2π rad",
      "d": "0 rad"
    },
    "answer": "c",
    "explanation": "One full wavelength corresponds to one complete cycle, which equals a phase difference of 2π radians (360°)."
  },
  {
    "id": 204,
    "topic": "Fluid Mechanics – Pascal's Law Applications",
    "question": "Hydraulic brakes work on the principle of:",
    "options": {
      "a": "Bernoulli's theorem",
      "b": "Pascal's law",
      "c": "Archimedes' principle",
      "d": "Newton's third law"
    },
    "answer": "b",
    "explanation": "Hydraulic brakes transmit pressure equally in all directions through an enclosed fluid (Pascal's law), multiplying the braking force."
  },
  {
    "id": 205,
    "topic": "Fluid Mechanics – Hydrostatic Paradox",
    "question": "The hydrostatic pressure at a given depth in a liquid depends on:",
    "options": {
      "a": "The shape of the container",
      "b": "The volume of the liquid",
      "c": "Only the depth and density of the liquid",
      "d": "The total weight of liquid above"
    },
    "answer": "c",
    "explanation": "Hydrostatic paradox: P = ρgh depends only on depth h and density ρ, not on container shape or total volume. This is why dams must be strong at the base regardless of reservoir shape."
  },
  {
    "id": 206,
    "topic": "Thermodynamics – Cp and Cv",
    "question": "For an ideal gas, Cp − Cv equals:",
    "options": {
      "a": "0",
      "b": "R/2",
      "c": "R",
      "d": "2R"
    },
    "answer": "c",
    "explanation": "For an ideal gas, Cp − Cv = R (universal gas constant). This is the Mayer relation, arising because extra work PΔV = nRT is done during constant pressure heating."
  },
  {
    "id": 207,
    "topic": "Thermodynamics – Cp and Cv",
    "question": "For a monatomic ideal gas, Cv equals:",
    "options": {
      "a": "R/2",
      "b": "R",
      "c": "3R/2",
      "d": "5R/2"
    },
    "answer": "c",
    "explanation": "A monatomic ideal gas has 3 translational degrees of freedom. By equipartition: Cv = (3/2)R."
  },
  {
    "id": 208,
    "topic": "Thermodynamics – Cp and Cv",
    "question": "For a diatomic ideal gas at moderate temperatures, the ratio γ = Cp/Cv is:",
    "options": {
      "a": "5/3",
      "b": "7/5",
      "c": "4/3",
      "d": "3/2"
    },
    "answer": "b",
    "explanation": "Diatomic gas: Cv = (5/2)R (3 translational + 2 rotational), Cp = (7/2)R. γ = Cp/Cv = 7/5 = 1.4"
  },
  {
    "id": 209,
    "topic": "Waves – Sound Intensity",
    "question": "Sound intensity level is measured in:",
    "options": {
      "a": "Hertz",
      "b": "Decibels",
      "c": "Pascals",
      "d": "Watts"
    },
    "answer": "b",
    "explanation": "Sound intensity level L = 10 log₁₀(I/I₀) is measured in decibels (dB), where I₀ = 10⁻¹² W/m² is the threshold of hearing."
  },
  {
    "id": 210,
    "topic": "Waves – Sound Intensity",
    "question": "If sound intensity doubles, the intensity level change in decibels is approximately:",
    "options": {
      "a": "1 dB",
      "b": "2 dB",
      "c": "3 dB",
      "d": "6 dB"
    },
    "answer": "c",
    "explanation": "ΔL = 10 log₁₀(2I/I) = 10 log₁₀(2) ≈ 10 × 0.301 ≈ 3 dB. Doubling intensity ≈ +3 dB."
  },
  {
    "id": 211,
    "topic": "Fluid Mechanics – Buoyancy",
    "question": "An object floats when:",
    "options": {
      "a": "Its density equals the liquid density",
      "b": "Its weight equals the buoyant force",
      "c": "Its density is less than the liquid density",
      "d": "Both b and c"
    },
    "answer": "d",
    "explanation": "An object floats when buoyant force = weight. This occurs when average density ≤ liquid density. Both statements (b) and (c) describe this condition."
  },
  {
    "id": 212,
    "topic": "Elasticity – Springs",
    "question": "Two springs with spring constants k₁ and k₂ are connected in series. The effective spring constant is:",
    "options": {
      "a": "k₁ + k₂",
      "b": "k₁k₂/(k₁ + k₂)",
      "c": "√(k₁k₂)",
      "d": "(k₁ + k₂)/2"
    },
    "answer": "b",
    "explanation": "Springs in series: 1/k_eff = 1/k₁ + 1/k₂ → k_eff = k₁k₂/(k₁ + k₂). The softer spring dominates."
  },
  {
    "id": 213,
    "topic": "Elasticity – Springs",
    "question": "Two springs with spring constants k₁ and k₂ are connected in parallel. The effective spring constant is:",
    "options": {
      "a": "k₁ + k₂",
      "b": "k₁k₂/(k₁ + k₂)",
      "c": "(k₁ − k₂)/2",
      "d": "k₁/k₂"
    },
    "answer": "a",
    "explanation": "Springs in parallel: k_eff = k₁ + k₂. Both springs share the load and both extend the same amount."
  },
  {
    "id": 214,
    "topic": "Waves – SHM Energy",
    "question": "In SHM, total mechanical energy is:",
    "options": {
      "a": "Entirely kinetic at maximum displacement",
      "b": "Entirely potential at equilibrium",
      "c": "Constant throughout the motion",
      "d": "Zero at maximum displacement"
    },
    "answer": "c",
    "explanation": "In SHM: E_total = ½kA² = constant. At equilibrium, all energy is kinetic; at maximum displacement, all energy is potential. The total remains constant."
  },
  {
    "id": 215,
    "topic": "Waves – SHM Velocity",
    "question": "In SHM, velocity is maximum at:",
    "options": {
      "a": "Maximum displacement (amplitude)",
      "b": "Equilibrium position",
      "c": "Half the amplitude",
      "d": "Quarter period after maximum displacement"
    },
    "answer": "b",
    "explanation": "v = ω√(A² − x²). At equilibrium (x = 0): v_max = ωA. At maximum displacement (x = A): v = 0."
  },
  {
    "id": 216,
    "topic": "Thermodynamics – Zeroth Law",
    "question": "The Zeroth Law of Thermodynamics is the basis for:",
    "options": {
      "a": "Conservation of energy",
      "b": "The concept of temperature and thermometers",
      "c": "Entropy increase",
      "d": "Absolute zero temperature"
    },
    "answer": "b",
    "explanation": "The Zeroth Law: if A is in thermal equilibrium with B, and B with C, then A is in equilibrium with C. This defines temperature and justifies thermometers."
  },
  {
    "id": 217,
    "topic": "Thermodynamics – Third Law",
    "question": "The Third Law of Thermodynamics states that:",
    "options": {
      "a": "Entropy increases in isolated systems",
      "b": "Energy is conserved",
      "c": "Entropy of a perfect crystal approaches zero at absolute zero",
      "d": "Heat cannot flow from cold to hot spontaneously"
    },
    "answer": "c",
    "explanation": "Third Law (Nernst theorem): As T → 0 K, the entropy of a perfectly ordered crystal approaches zero. Absolute zero is unattainable."
  },
  {
    "id": 218,
    "topic": "Fluid Mechanics – Pitot Tube",
    "question": "A Pitot tube measures:",
    "options": {
      "a": "Fluid viscosity",
      "b": "Static pressure only",
      "c": "Fluid flow velocity",
      "d": "Temperature of flowing fluid"
    },
    "answer": "c",
    "explanation": "A Pitot tube measures the stagnation pressure of a flowing fluid. By comparing stagnation and static pressure using Bernoulli's equation, fluid velocity can be determined."
  },
  {
    "id": 219,
    "topic": "Surface Tension – Soap Film",
    "question": "A rectangular wire frame with a slider (length 5 cm) is pulled to stretch a soap film. If T = 0.04 N/m, the force needed (considering two surfaces) is:",
    "options": {
      "a": "0.001 N",
      "b": "0.002 N",
      "c": "0.004 N",
      "d": "0.008 N"
    },
    "answer": "c",
    "explanation": "F = T × 2L (soap film has two surfaces) = 0.04 × 2 × 0.05 = 0.004 N"
  },
  {
    "id": 220,
    "topic": "Waves – Diffraction",
    "question": "Diffraction of waves is most pronounced when the wavelength is:",
    "options": {
      "a": "Much smaller than the obstacle/slit",
      "b": "Comparable to the size of the obstacle/slit",
      "c": "Much larger than the obstacle/slit",
      "d": "Equal to twice the obstacle size"
    },
    "answer": "b",
    "explanation": "Diffraction is most significant when wavelength ≈ slit/obstacle size. Very long wavelengths show spreading, but maximum diffraction effects occur at comparable dimensions."
  },
  {
    "id": 221,
    "topic": "Thermodynamics – Internal Energy",
    "question": "The internal energy of an ideal gas depends only on:",
    "options": {
      "a": "Pressure",
      "b": "Volume",
      "c": "Temperature",
      "d": "Both pressure and volume"
    },
    "answer": "c",
    "explanation": "For an ideal gas, internal energy U = nCvT depends only on temperature. This is because ideal gas molecules have no intermolecular potential energy."
  },
  {
    "id": 222,
    "topic": "Fluid Mechanics – Surface Tension vs Viscosity",
    "question": "Which property resists the flow of a fluid between layers moving at different velocities?",
    "options": {
      "a": "Surface tension",
      "b": "Viscosity",
      "c": "Density",
      "d": "Compressibility"
    },
    "answer": "b",
    "explanation": "Viscosity is the internal friction of a fluid that resists relative motion between adjacent fluid layers. Surface tension acts at the liquid surface, not between internal layers."
  },
  {
    "id": 223,
    "topic": "Waves – Interference",
    "question": "Constructive interference occurs when two waves meet with a path difference of:",
    "options": {
      "a": "λ/2",
      "b": "λ",
      "c": "3λ/4",
      "d": "λ/4"
    },
    "answer": "b",
    "explanation": "Constructive interference requires path difference = nλ (n = 0, 1, 2, ...), giving phase difference = 2nπ. The waves add up maximally."
  },
  {
    "id": 224,
    "topic": "Waves – Interference",
    "question": "Destructive interference occurs when path difference is:",
    "options": {
      "a": "nλ",
      "b": "(2n+1)λ/2",
      "c": "nλ/2",
      "d": "2nλ"
    },
    "answer": "b",
    "explanation": "Destructive interference: path difference = (2n+1)λ/2 = λ/2, 3λ/2, 5λ/2, ... The waves cancel completely if amplitudes are equal."
  },
  {
    "id": 225,
    "topic": "Fluid Mechanics – Specific Gravity",
    "question": "Specific gravity (relative density) of a substance is defined as:",
    "options": {
      "a": "Mass per unit volume",
      "b": "Ratio of its density to density of water at 4°C",
      "c": "Weight per unit volume",
      "d": "Ratio of volume to mass"
    },
    "answer": "b",
    "explanation": "Specific gravity = ρ_substance/ρ_water(4°C). It is dimensionless. For water SG = 1; for mercury SG ≈ 13.6."
  },
  {
    "id": 226,
    "topic": "Thermodynamics – Work by Gas",
    "question": "Work done by a gas in an isobaric (constant pressure) expansion from V₁ to V₂ is:",
    "options": {
      "a": "P(V₂ − V₁)",
      "b": "V(P₂ − P₁)",
      "c": "nRTln(V₂/V₁)",
      "d": "Zero"
    },
    "answer": "a",
    "explanation": "W = ∫PdV = P∫dV = P(V₂ − V₁) at constant pressure. For isothermal: W = nRTln(V₂/V₁)."
  },
  {
    "id": 227,
    "topic": "Elasticity – Factor of Safety",
    "question": "Factor of safety in engineering design is defined as:",
    "options": {
      "a": "Working stress / Ultimate stress",
      "b": "Ultimate stress / Working stress",
      "c": "Elastic modulus / Yield stress",
      "d": "Strain / Stress"
    },
    "answer": "b",
    "explanation": "Factor of Safety = Ultimate (or yield) stress / Allowable (working) stress. A higher factor of safety means a more conservative, safer design."
  },
  {
    "id": 228,
    "topic": "Fluid Mechanics – Pressure Units",
    "question": "Standard atmospheric pressure is approximately:",
    "options": {
      "a": "1000 Pa",
      "b": "10⁵ Pa",
      "c": "10⁶ Pa",
      "d": "10⁴ Pa"
    },
    "answer": "b",
    "explanation": "1 atm = 101,325 Pa ≈ 1.013 × 10⁵ Pa ≈ 10⁵ Pa. This equals the pressure exerted by a 760 mm column of mercury."
  },
  {
    "id": 229,
    "topic": "Thermodynamics – Kelvin Scale",
    "question": "The Kelvin scale is related to Celsius by:",
    "options": {
      "a": "T(K) = T(°C) + 100",
      "b": "T(K) = T(°C) − 273.15",
      "c": "T(K) = T(°C) + 273.15",
      "d": "T(K) = T(°C) × 1.8 + 32"
    },
    "answer": "c",
    "explanation": "T(K) = T(°C) + 273.15. The Kelvin scale starts at absolute zero (−273.15°C). It is the SI temperature scale."
  },
  {
    "id": 230,
    "topic": "Waves – Transverse Wave Properties",
    "question": "Which of the following waves is NOT a transverse wave?",
    "options": {
      "a": "Light waves",
      "b": "Water surface waves",
      "c": "Sound waves in air",
      "d": "Waves on a string"
    },
    "answer": "c",
    "explanation": "Sound waves in air are longitudinal — particles vibrate parallel to propagation direction. Light, water surface, and string waves are transverse."
  },
  {
    "id": 231,
    "topic": "Fluid Mechanics – Ideal Fluid",
    "question": "An ideal fluid is characterized as:",
    "options": {
      "a": "Viscous and compressible",
      "b": "Non-viscous and compressible",
      "c": "Non-viscous and incompressible",
      "d": "Viscous and incompressible"
    },
    "answer": "c",
    "explanation": "An ideal fluid is: (1) non-viscous (no internal friction), (2) incompressible (constant density), and (3) has steady, irrotational flow. Real fluids deviate from this."
  },
  {
    "id": 232,
    "topic": "Elasticity – Rigidity",
    "question": "Which type of stress causes a change in shape without change in volume?",
    "options": {
      "a": "Compressive stress",
      "b": "Tensile stress",
      "c": "Shear stress",
      "d": "Hydrostatic stress"
    },
    "answer": "c",
    "explanation": "Shear stress causes angular deformation (change in shape) at constant volume. Hydrostatic stress causes volume change without shape change."
  },
  {
    "id": 233,
    "topic": "Thermodynamics – Heat Capacity",
    "question": "Water has a very high specific heat capacity. This means water:",
    "options": {
      "a": "Heats up and cools down quickly",
      "b": "Stores large amounts of heat for small temperature changes",
      "c": "Conducts heat very well",
      "d": "Has low boiling point"
    },
    "answer": "b",
    "explanation": "High specific heat (4200 J/kg·K) means water requires a lot of energy to change temperature. This makes it excellent for storing thermal energy and moderating climate."
  },
  {
    "id": 234,
    "topic": "Waves – Speed in Medium",
    "question": "The speed of sound is greatest in:",
    "options": {
      "a": "Air at 0°C",
      "b": "Water",
      "c": "Steel",
      "d": "Vacuum"
    },
    "answer": "c",
    "explanation": "Speed of sound: air ≈ 340 m/s, water ≈ 1480 m/s, steel ≈ 5000 m/s. Speed increases with bulk modulus and decreases with density. Steel has very high stiffness."
  },
  {
    "id": 235,
    "topic": "Surface Tension – Molecular Explanation",
    "question": "A molecule at the surface of a liquid experiences a net force:",
    "options": {
      "a": "Directed outward from the liquid",
      "b": "Directed into the bulk of the liquid",
      "c": "Perpendicular to the surface outward",
      "d": "Zero, same as interior molecules"
    },
    "answer": "b",
    "explanation": "Surface molecules are attracted by molecules below and to the sides but not from above (no liquid above). The net intermolecular force is directed inward into the bulk."
  },
  {
    "id": 236,
    "topic": "Thermodynamics – Free Expansion",
    "question": "In a free expansion of an ideal gas into a vacuum:",
    "options": {
      "a": "Temperature drops",
      "b": "Temperature rises",
      "c": "Temperature remains constant",
      "d": "Pressure increases"
    },
    "answer": "c",
    "explanation": "In free expansion into vacuum: W = 0 (no external pressure), Q = 0 (insulated). So ΔU = 0, and for ideal gas U depends only on T → T remains constant."
  },
  {
    "id": 237,
    "topic": "Fluid Mechanics – Viscous Flow",
    "question": "Viscosity of a liquid generally:",
    "options": {
      "a": "Increases with temperature",
      "b": "Decreases with temperature",
      "c": "Is independent of temperature",
      "d": "First decreases then increases with temperature"
    },
    "answer": "b",
    "explanation": "Liquid viscosity decreases with increasing temperature because higher thermal energy overcomes intermolecular attractions between layers. (Note: gas viscosity increases with temperature — opposite behavior.)"
  },
  {
    "id": 238,
    "topic": "Waves – Resonance in Pipes",
    "question": "A closed pipe of length 34 cm resonates at its fundamental frequency. The frequency is: (v_sound = 340 m/s)",
    "options": {
      "a": "250 Hz",
      "b": "500 Hz",
      "c": "1000 Hz",
      "d": "125 Hz"
    },
    "answer": "a",
    "explanation": "Closed pipe: f = v/4L = 340/(4 × 0.34) = 340/1.36 = 250 Hz"
  },
  {
    "id": 239,
    "topic": "Waves – Open Pipe",
    "question": "An open pipe of length 34 cm resonates at its fundamental frequency. The frequency is: (v_sound = 340 m/s)",
    "options": {
      "a": "250 Hz",
      "b": "500 Hz",
      "c": "1000 Hz",
      "d": "125 Hz"
    },
    "answer": "b",
    "explanation": "Open pipe: f = v/2L = 340/(2 × 0.34) = 340/0.68 = 500 Hz"
  },
  {
    "id": 240,
    "topic": "Elasticity – Wire Elongation",
    "question": "A copper wire (Y = 1.2×10¹¹ Pa) of length 1 m and cross-section 1 mm² stretches by 0.1 mm under a load. The applied force is:",
    "options": {
      "a": "12 N",
      "b": "120 N",
      "c": "1200 N",
      "d": "12000 N"
    },
    "answer": "a",
    "explanation": "Y = FL/(AΔL) → F = YAΔl/L = 1.2×10¹¹ × 10⁻⁶ × 0.0001/1 = 1.2×10¹¹ × 10⁻¹⁰ = 12 N"
  },
  {
    "id": 241,
    "topic": "Thermodynamics – Polytropic Process",
    "question": "An isothermal process for an ideal gas satisfies PVⁿ = constant where n =",
    "options": {
      "a": "0",
      "b": "1",
      "c": "γ",
      "d": "∞"
    },
    "answer": "b",
    "explanation": "Polytropic process: PVⁿ = constant. n=0: isobaric; n=1: isothermal; n=γ: adiabatic; n=∞: isochoric."
  },
  {
    "id": 242,
    "topic": "Thermodynamics – Thermal Expansion",
    "question": "A steel rod of length 1 m expands by 1.2 mm when temperature rises by 100°C. The coefficient of linear expansion is:",
    "options": {
      "a": "1.2×10⁻⁴ /°C",
      "b": "1.2×10⁻⁵ /°C",
      "c": "1.2×10⁻³ /°C",
      "d": "1.2×10⁻² /°C"
    },
    "answer": "b",
    "explanation": "α = ΔL/(L·ΔT) = 0.0012/(1 × 100) = 1.2×10⁻⁵ /°C"
  },
  {
    "id": 243,
    "topic": "Thermodynamics – Thermal Expansion",
    "question": "The coefficient of volumetric expansion γ is related to the linear expansion coefficient α by:",
    "options": {
      "a": "γ = α",
      "b": "γ = 2α",
      "c": "γ = 3α",
      "d": "γ = α²"
    },
    "answer": "c",
    "explanation": "For isotropic materials: γ = 3α (volumetric = 3 × linear). Similarly, the area expansion coefficient β = 2α."
  },
  {
    "id": 244,
    "topic": "Fluid Mechanics – Manometer",
    "question": "A U-tube manometer measures:",
    "options": {
      "a": "Flow velocity",
      "b": "Gauge pressure difference between two points",
      "c": "Fluid viscosity",
      "d": "Surface tension"
    },
    "answer": "b",
    "explanation": "A U-tube manometer compares pressures at two points. The height difference of liquid columns indicates the gauge pressure difference between them."
  },
  {
    "id": 245,
    "topic": "Waves – Polarization",
    "question": "Polarization is a property of:",
    "options": {
      "a": "Longitudinal waves only",
      "b": "Transverse waves only",
      "c": "Both longitudinal and transverse waves",
      "d": "Sound waves only"
    },
    "answer": "b",
    "explanation": "Only transverse waves can be polarized (vibration restricted to one plane). Longitudinal waves (like sound) oscillate along the propagation direction and cannot be polarized."
  },
  {
    "id": 246,
    "topic": "Surface Tension – Detergent Effect",
    "question": "Adding detergent (surfactant) to water:",
    "options": {
      "a": "Increases surface tension",
      "b": "Has no effect on surface tension",
      "c": "Reduces surface tension",
      "d": "Makes water solidify"
    },
    "answer": "c",
    "explanation": "Surfactants (surface-active agents) disrupt hydrogen bonds at the water surface, reducing surface tension. This is why detergents clean better — water can spread more and wet surfaces."
  },
  {
    "id": 247,
    "topic": "Elasticity – Bending of Beams",
    "question": "A beam that is fixed at one end and free at the other is called a:",
    "options": {
      "a": "Simply supported beam",
      "b": "Cantilever beam",
      "c": "Propped beam",
      "d": "Continuous beam"
    },
    "answer": "b",
    "explanation": "A cantilever beam is fixed (clamped) at one end and free at the other. It deflects under load and is common in balconies, aircraft wings, and bridge supports."
  },
  {
    "id": 248,
    "topic": "Thermodynamics – Efficiency",
    "question": "The efficiency of a real heat engine is always:",
    "options": {
      "a": "Equal to Carnot efficiency",
      "b": "Greater than Carnot efficiency",
      "c": "Less than Carnot efficiency",
      "d": "100%"
    },
    "answer": "c",
    "explanation": "No real engine can achieve Carnot efficiency due to irreversibilities (friction, heat losses). Carnot efficiency is the theoretical maximum for engines operating between two temperatures."
  },
  {
    "id": 249,
    "topic": "Fluid Mechanics – Cohesion and Adhesion",
    "question": "The force of attraction between molecules of the SAME substance is called:",
    "options": {
      "a": "Adhesion",
      "b": "Cohesion",
      "c": "Surface tension",
      "d": "Viscous force"
    },
    "answer": "b",
    "explanation": "Cohesion = intermolecular attraction between like molecules (e.g., water–water). Adhesion = attraction between different substances (e.g., water–glass)."
  },
  {
    "id": 250,
    "topic": "Waves – Stationary Waves",
    "question": "In a stationary wave, the distance between two adjacent nodes is:",
    "options": {
      "a": "λ",
      "b": "λ/4",
      "c": "λ/2",
      "d": "2λ"
    },
    "answer": "c",
    "explanation": "In a standing wave, nodes occur every half wavelength: distance between adjacent nodes = λ/2. Antinodes are midway between nodes."
  },
  {
    "id": 251,
    "topic": "Thermodynamics – Clausius Statement",
    "question": "The Clausius statement of the Second Law says:",
    "options": {
      "a": "No engine is 100% efficient",
      "b": "Heat cannot spontaneously flow from cold to hot body",
      "c": "Entropy always decreases",
      "d": "Energy is always conserved"
    },
    "answer": "b",
    "explanation": "Clausius: 'It is impossible to transfer heat from a colder body to a warmer one without external work.' This is equivalent to Kelvin's statement about heat engines."
  },
  {
    "id": 252,
    "topic": "Fluid Mechanics – Density",
    "question": "The density of a substance is defined as:",
    "options": {
      "a": "Mass × Volume",
      "b": "Mass / Volume",
      "c": "Weight / Mass",
      "d": "Volume / Mass"
    },
    "answer": "b",
    "explanation": "Density ρ = m/V (mass per unit volume). SI unit is kg/m³. It is an intensive property (does not depend on amount of substance)."
  },
  {
    "id": 253,
    "topic": "Waves – Speed of Sound",
    "question": "The speed of sound increases with temperature because:",
    "options": {
      "a": "Air density increases with temperature",
      "b": "Molecular speed increases, increasing bulk modulus effectively",
      "c": "Wavelength increases while frequency stays constant",
      "d": "Sound becomes electromagnetic at higher temperatures"
    },
    "answer": "b",
    "explanation": "v = √(γRT/M). Speed of sound ∝ √T. Higher temperature → faster molecules → more rapid pressure propagation. v ≈ 331√(T/273) m/s."
  },
  {
    "id": 254,
    "topic": "Elasticity – Wire Under Load",
    "question": "A wire elongates by 1 mm under a 10 N load. How much will it elongate under a 30 N load (within elastic limit)?",
    "options": {
      "a": "1 mm",
      "b": "2 mm",
      "c": "3 mm",
      "d": "10 mm"
    },
    "answer": "c",
    "explanation": "By Hooke's Law, extension is proportional to load within the elastic limit. ΔL ∝ F → ΔL₂ = ΔL₁ × (F₂/F₁) = 1 × (30/10) = 3 mm."
  },
  {
    "id": 255,
    "topic": "Thermodynamics – Saturated Vapor",
    "question": "At the boiling point, a liquid:",
    "options": {
      "a": "Absorbs heat and temperature rises",
      "b": "Releases heat at constant temperature",
      "c": "Absorbs heat at constant temperature",
      "d": "Changes directly to gas without heat input"
    },
    "answer": "c",
    "explanation": "At boiling point, absorbed heat (latent heat of vaporization) goes into breaking intermolecular bonds to convert liquid to vapor. Temperature stays constant during the phase change."
  },
  {
    "id": 256,
    "topic": "Fluid Mechanics – Capillary Tube",
    "question": "If a capillary tube is dipped in a liquid that does not wet it (contact angle > 90°), the liquid level inside the tube:",
    "options": {
      "a": "Rises above outside level",
      "b": "Falls below outside level",
      "c": "Stays at the same level",
      "d": "Oscillates up and down"
    },
    "answer": "b",
    "explanation": "For non-wetting liquids (θ > 90°), cosθ < 0, so h = 2Tcosθ/(ρgr) < 0 — liquid is depressed below the outside level. Example: mercury in glass."
  },
  {
    "id": 257,
    "topic": "Waves – Forced Vibration",
    "question": "In forced vibration, the body eventually vibrates at:",
    "options": {
      "a": "Its natural frequency",
      "b": "The frequency of the applied force",
      "c": "Zero frequency",
      "d": "The average of natural and applied frequencies"
    },
    "answer": "b",
    "explanation": "In forced (driven) vibration, after transients die out, the system vibrates at the frequency of the driving force, regardless of its own natural frequency."
  },
  {
    "id": 258,
    "topic": "Thermodynamics – Mean Free Path",
    "question": "The mean free path of a gas molecule is the:",
    "options": {
      "a": "Total distance traveled per second",
      "b": "Average distance between successive collisions",
      "c": "Maximum speed of molecules",
      "d": "Diameter of the molecule"
    },
    "answer": "b",
    "explanation": "Mean free path λ = 1/(√2·π·d²·n), where d is molecular diameter and n is number density. It is the average distance a molecule travels between consecutive collisions."
  },
  {
    "id": 259,
    "topic": "Thermodynamics – Kinetic Theory",
    "question": "The average kinetic energy of a gas molecule at temperature T is:",
    "options": {
      "a": "½k_BT",
      "b": "k_BT",
      "c": "3k_BT/2",
      "d": "3k_BT"
    },
    "answer": "c",
    "explanation": "By equipartition: average KE per molecule = (3/2)k_BT for monatomic gas (3 translational degrees of freedom). k_B = 1.38×10⁻²³ J/K."
  },
  {
    "id": 260,
    "topic": "Thermodynamics – RMS Speed",
    "question": "The rms speed of gas molecules is:",
    "options": {
      "a": "√(RT/M)",
      "b": "√(2RT/M)",
      "c": "√(3RT/M)",
      "d": "√(8RT/πM)"
    },
    "answer": "c",
    "explanation": "v_rms = √(3RT/M) = √(3k_BT/m). Note: v_avg = √(8RT/πM), v_mp = √(2RT/M). v_rms > v_avg > v_mp."
  },
  {
    "id": 261,
    "topic": "Waves – Echo",
    "question": "For a person to hear a distinct echo, the minimum distance from a reflecting surface should be: (v_sound = 340 m/s, minimum time to distinguish = 0.1 s)",
    "options": {
      "a": "8.5 m",
      "b": "17 m",
      "c": "34 m",
      "d": "3.4 m"
    },
    "answer": "b",
    "explanation": "Sound travels to wall and back: d = v·t/2 = 340 × 0.1/2 = 17 m. The minimum distance for a distinct echo is 17 m."
  },
  {
    "id": 262,
    "topic": "Elasticity – Poisson's Ratio Range",
    "question": "For most engineering materials, Poisson's ratio lies in the range:",
    "options": {
      "a": "0 to 0.5",
      "b": "0.5 to 1.0",
      "c": "1.0 to 2.0",
      "d": "−1 to 0"
    },
    "answer": "a",
    "explanation": "For stable isotropic materials, 0 < ν < 0.5. Rubber ≈ 0.49 (nearly incompressible), cork ≈ 0, steel ≈ 0.3. Negative ν is possible only in special auxetic materials."
  },
  {
    "id": 263,
    "topic": "Fluid Mechanics – Pressure on Walls",
    "question": "A dam holds water to a height H. The average pressure on the dam face is:",
    "options": {
      "a": "ρgH",
      "b": "ρgH/2",
      "c": "ρgH/3",
      "d": "2ρgH"
    },
    "answer": "b",
    "explanation": "Pressure varies linearly from 0 at top to ρgH at bottom. Average pressure = ρgH/2. Total force = average pressure × area = ρgH/2 × A."
  },
  {
    "id": 264,
    "topic": "Thermodynamics – Phase Diagram",
    "question": "The triple point of a substance is where:",
    "options": {
      "a": "All three states are in equilibrium simultaneously",
      "b": "Only liquid and gas coexist",
      "c": "Critical pressure is reached",
      "d": "The substance sublimes"
    },
    "answer": "a",
    "explanation": "At the triple point, specific temperature and pressure allow solid, liquid, and vapor to coexist in equilibrium. For water: T = 273.16 K, P = 611.73 Pa."
  },
  {
    "id": 265,
    "topic": "Thermodynamics – Critical Point",
    "question": "Above the critical temperature:",
    "options": {
      "a": "A gas can always be liquefied by pressure",
      "b": "A gas cannot be liquefied by pressure alone",
      "c": "The substance is always solid",
      "d": "The substance always sublimes"
    },
    "answer": "b",
    "explanation": "Above the critical temperature T_c, no amount of pressure can liquefy a gas — the distinction between liquid and gas phases disappears. The substance exists as a supercritical fluid."
  },
  {
    "id": 266,
    "topic": "Waves – Musical Instruments",
    "question": "A guitar string vibrates at 440 Hz (A4). If it is shortened to half its length (tension constant), the new frequency is:",
    "options": {
      "a": "220 Hz",
      "b": "440 Hz",
      "c": "880 Hz",
      "d": "1320 Hz"
    },
    "answer": "c",
    "explanation": "f = (1/2L)√(T/μ). Halving L doubles frequency: f_new = 2 × 440 = 880 Hz. This is why pressing a fret raises pitch."
  },
  {
    "id": 267,
    "topic": "Surface Tension – Pressure at Curved Surface",
    "question": "For a cylindrical bubble (like a soap cylinder), the excess pressure inside is:",
    "options": {
      "a": "4T/R",
      "b": "2T/R",
      "c": "T/R",
      "d": "T/(2R)"
    },
    "answer": "b",
    "explanation": "A cylindrical bubble has curvature in only one direction: ΔP = 2T/R (for a soap cylinder with 2 surfaces: ΔP = 4T/R? Actually for a long cylindrical soap film: pressure from one surface curvature = T/R each, total 2T/R). The standard result for a cylinder is 2T/R."
  },
  {
    "id": 268,
    "topic": "Thermodynamics – Joule-Thomson Effect",
    "question": "In the Joule-Thomson effect, a real gas expands through a porous plug. For most gases below the inversion temperature, the temperature:",
    "options": {
      "a": "Increases",
      "b": "Decreases",
      "c": "Remains constant",
      "d": "First increases then decreases"
    },
    "answer": "b",
    "explanation": "Below the inversion temperature, the Joule-Thomson effect causes cooling during throttling (intermolecular attraction dominates). This is the basis of gas liquefaction."
  },
  {
    "id": 269,
    "topic": "Waves – Melde's Experiment",
    "question": "In Melde's experiment, the frequency of vibration of a string is proportional to:",
    "options": {
      "a": "√(Tension)",
      "b": "1/√(linear mass density)",
      "c": "Both a and b",
      "d": "Length of string"
    },
    "answer": "c",
    "explanation": "f = (n/2L)√(T/μ). Frequency is proportional to √T and to 1/√μ (linear mass density). Both a and b are correct."
  },
  {
    "id": 270,
    "topic": "Elasticity – Elastic and Plastic",
    "question": "A rubber band stretched beyond recovery has undergone:",
    "options": {
      "a": "Elastic deformation",
      "b": "Plastic deformation",
      "c": "Viscous deformation",
      "d": "No deformation"
    },
    "answer": "b",
    "explanation": "Once stretched beyond the elastic limit, the rubber has plastic (permanent) deformation — it will not return to its original length upon release."
  },
  {
    "id": 271,
    "topic": "Thermodynamics – Enthalpy",
    "question": "Enthalpy H is defined as:",
    "options": {
      "a": "H = U − PV",
      "b": "H = U + PV",
      "c": "H = U + TS",
      "d": "H = G + TS"
    },
    "answer": "b",
    "explanation": "Enthalpy H = U + PV. At constant pressure, ΔH = Q_p (heat at constant pressure). Enthalpy is useful for chemical reactions and phase transitions."
  },
  {
    "id": 272,
    "topic": "Fluid Mechanics – Torque on a Dam",
    "question": "The center of pressure on a vertical rectangular dam face (height H, submerged from top) is at a depth of:",
    "options": {
      "a": "H/2",
      "b": "H/3",
      "c": "2H/3",
      "d": "H/4"
    },
    "answer": "c",
    "explanation": "Center of pressure for a vertical rectangle submerged to height H from the surface: depth = 2H/3. The resultant force acts at 2H/3 from the top (or H/3 from the bottom)."
  },
  {
    "id": 273,
    "topic": "Waves – Ultrasound",
    "question": "Ultrasound has frequencies:",
    "options": {
      "a": "Below 20 Hz",
      "b": "Between 20 Hz and 20 kHz",
      "c": "Above 20 kHz",
      "d": "Above 1 GHz"
    },
    "answer": "c",
    "explanation": "Ultrasound: f > 20,000 Hz (20 kHz), above the upper limit of human hearing. Infrasound: f < 20 Hz. Audible range: 20 Hz – 20 kHz."
  },
  {
    "id": 274,
    "topic": "Thermodynamics – Vaporization",
    "question": "Evaporation occurs:",
    "options": {
      "a": "Only at the boiling point",
      "b": "At all temperatures from the surface of a liquid",
      "c": "Only above the boiling point",
      "d": "Only in vacuum"
    },
    "answer": "b",
    "explanation": "Evaporation (surface phenomenon) occurs at any temperature as high-energy surface molecules escape. Boiling occurs throughout the liquid only at the boiling point."
  },
  {
    "id": 275,
    "topic": "Fluid Mechanics – Orifice",
    "question": "The coefficient of discharge for an orifice is defined as:",
    "options": {
      "a": "Theoretical velocity / Actual velocity",
      "b": "Actual discharge / Theoretical discharge",
      "c": "Actual area / Orifice area",
      "d": "Pressure / Velocity"
    },
    "answer": "b",
    "explanation": "Cd = actual discharge / theoretical discharge = Cc × Cv, where Cc is coefficient of contraction and Cv is coefficient of velocity. Typically Cd ≈ 0.6 for sharp-edged orifice."
  },
  {
    "id": 276,
    "topic": "Waves – Resonance Examples",
    "question": "Which of the following is NOT a practical application of resonance?",
    "options": {
      "a": "Tuning of radio/TV receivers",
      "b": "MRI machines",
      "c": "Microwave heating",
      "d": "Newton's cradle"
    },
    "answer": "d",
    "explanation": "Radio/TV tuning, MRI (nuclear magnetic resonance), and microwave heating all use resonance phenomena. Newton's cradle demonstrates conservation of momentum/energy, not resonance."
  },
  {
    "id": 277,
    "topic": "Thermodynamics – Calorimetry",
    "question": "The principle of calorimetry states:",
    "options": {
      "a": "Heat lost = Heat gained for mixed substances",
      "b": "Total energy is converted to heat",
      "c": "Mass × specific heat = temperature change",
      "d": "Heat capacity is constant for all materials"
    },
    "answer": "a",
    "explanation": "Principle of calorimetry (method of mixtures): heat lost by hot body = heat gained by cold body, when no heat is lost to surroundings."
  },
  {
    "id": 278,
    "topic": "Thermodynamics – Kelvin-Celsius",
    "question": "A body has a temperature of 77 K. Its temperature in °C is:",
    "options": {
      "a": "−196°C",
      "b": "−273°C",
      "c": "77°C",
      "d": "350°C"
    },
    "answer": "a",
    "explanation": "T(°C) = T(K) − 273 = 77 − 273 = −196°C. (This is the boiling point of liquid nitrogen.)"
  },
  {
    "id": 279,
    "topic": "Elasticity – Stress-Strain Diagram",
    "question": "On a stress-strain diagram, the region where stress is proportional to strain is called the:",
    "options": {
      "a": "Plastic region",
      "b": "Fracture zone",
      "c": "Proportional (elastic) region",
      "d": "Necking region"
    },
    "answer": "c",
    "explanation": "The initial linear portion of the stress-strain curve is the proportional/elastic region where Hooke's Law applies. Beyond the proportional limit, the relationship becomes non-linear."
  },
  {
    "id": 280,
    "topic": "Thermodynamics – Expansion Coefficient",
    "question": "A gas thermometer works because gas pressure at constant volume is:",
    "options": {
      "a": "Constant with temperature",
      "b": "Proportional to absolute temperature",
      "c": "Inversely proportional to temperature",
      "d": "Proportional to temperature squared"
    },
    "answer": "b",
    "explanation": "Gay-Lussac's Law (pressure law): at constant volume, P ∝ T (absolute temperature). P/T = constant. This forms the basis of constant-volume gas thermometers."
  },
  {
    "id": 281,
    "topic": "Fluid Mechanics – Streamlines and Pathlines",
    "question": "In steady flow, streamlines and pathlines:",
    "options": {
      "a": "Are always perpendicular",
      "b": "Coincide (are identical)",
      "c": "Never intersect",
      "d": "Have different shapes"
    },
    "answer": "b",
    "explanation": "In steady flow, the velocity at each point doesn't change with time. Therefore, every particle follows the same path, so streamlines and pathlines coincide."
  },
  {
    "id": 282,
    "topic": "Waves – Wave Number",
    "question": "Wave number k is defined as:",
    "options": {
      "a": "k = fλ",
      "b": "k = 2π/λ",
      "c": "k = λ/T",
      "d": "k = f/v"
    },
    "answer": "b",
    "explanation": "k = 2π/λ (rad/m). Wave number represents spatial frequency — cycles per unit length multiplied by 2π. Related to angular frequency: k = ω/v."
  },
  {
    "id": 283,
    "topic": "Thermodynamics – Absolute Zero",
    "question": "Absolute zero (0 K) is the temperature at which:",
    "options": {
      "a": "All molecular motion completely stops",
      "b": "A gas has zero volume",
      "c": "Molecules have minimum possible energy (zero-point energy remains)",
      "d": "Water freezes"
    },
    "answer": "c",
    "explanation": "At 0 K, classical kinetic energy → 0, but quantum zero-point energy remains. Molecular motion doesn't completely stop (quantum mechanics). It is the lowest possible temperature."
  },
  {
    "id": 284,
    "topic": "Fluid Mechanics – Metacenter",
    "question": "A floating body is in stable equilibrium when:",
    "options": {
      "a": "The center of gravity is above the metacenter",
      "b": "The metacenter is above the center of gravity",
      "c": "Center of gravity coincides with center of buoyancy",
      "d": "The body is fully submerged"
    },
    "answer": "b",
    "explanation": "Stable floating equilibrium requires the metacenter M to be above the center of gravity G. When tilted, the righting moment restores the body to equilibrium."
  },
  {
    "id": 285,
    "topic": "Waves – Standing Waves in String",
    "question": "Which of the following is NOT a mode of vibration of a string fixed at both ends?",
    "options": {
      "a": "1 loop (fundamental)",
      "b": "2 loops (2nd harmonic)",
      "c": "3 loops (3rd harmonic)",
      "d": "1.5 loops"
    },
    "answer": "d",
    "explanation": "Standing waves in strings fixed at both ends require integer numbers of half-wavelengths: n = 1, 2, 3, ... (complete loops). 1.5 loops would require a non-integer n and is not possible."
  },
  {
    "id": 286,
    "topic": "Thermodynamics – Enthalpy of Reaction",
    "question": "A reaction with negative enthalpy change (ΔH < 0) is:",
    "options": {
      "a": "Endothermic",
      "b": "Exothermic",
      "c": "Isothermal",
      "d": "Adiabatic"
    },
    "answer": "b",
    "explanation": "Exothermic reactions release heat to surroundings (ΔH < 0). Endothermic reactions absorb heat (ΔH > 0)."
  },
  {
    "id": 287,
    "topic": "Fluid Mechanics – Atmospheric Pressure",
    "question": "The height of mercury in a barometer at sea level is approximately:",
    "options": {
      "a": "10.3 m of water",
      "b": "760 mm of mercury",
      "c": "76 cm of mercury",
      "d": "Both b and c"
    },
    "answer": "d",
    "explanation": "Standard atmospheric pressure = 760 mm Hg = 76 cm Hg. These are the same value expressed differently. Also equivalent to 10.3 m of water."
  },
  {
    "id": 288,
    "topic": "Elasticity – Moduli Relationships",
    "question": "For an isotropic material, the relationship between E (Young's modulus), G (shear modulus), and ν (Poisson's ratio) is:",
    "options": {
      "a": "G = E/(1 + ν)",
      "b": "G = E/(2(1 + ν))",
      "c": "G = E·ν/(1 − 2ν)",
      "d": "G = 2E(1 + ν)"
    },
    "answer": "b",
    "explanation": "G = E/[2(1 + ν)]. For steel: E ≈ 200 GPa, ν ≈ 0.3, G = 200/[2(1.3)] ≈ 77 GPa."
  },
  {
    "id": 289,
    "topic": "Waves – Quality Factor",
    "question": "The quality factor Q of an oscillator describes:",
    "options": {
      "a": "The maximum amplitude of oscillation",
      "b": "The sharpness of resonance and rate of energy decay",
      "c": "The driving frequency",
      "d": "The damping velocity"
    },
    "answer": "b",
    "explanation": "Q = ω₀/Δω (resonant frequency / bandwidth). High Q: sharp resonance, slow energy decay (lightly damped). Low Q: broad resonance, rapid decay (heavily damped)."
  },
  {
    "id": 290,
    "topic": "Thermodynamics – Dalton's Law",
    "question": "Dalton's Law of Partial Pressures states that the total pressure of a gas mixture equals:",
    "options": {
      "a": "Product of partial pressures",
      "b": "Sum of partial pressures",
      "c": "Average of partial pressures",
      "d": "Largest partial pressure"
    },
    "answer": "b",
    "explanation": "P_total = P₁ + P₂ + P₃ + ... Each gas exerts pressure independently as if it alone occupied the container."
  },
  {
    "id": 291,
    "topic": "Fluid Mechanics – Viscometer",
    "question": "Viscosity is measured using a:",
    "options": {
      "a": "Manometer",
      "b": "Viscometer",
      "c": "Barometer",
      "d": "Hygrometer"
    },
    "answer": "b",
    "explanation": "A viscometer (or viscosimeter) measures the viscosity of fluids. Types include the Ostwald, Falling Ball, and Couette viscometers."
  },
  {
    "id": 292,
    "topic": "Waves – Acoustic Velocity in Solid",
    "question": "The speed of longitudinal waves in a solid rod is:",
    "options": {
      "a": "√(G/ρ)",
      "b": "√(E/ρ)",
      "c": "√(K/ρ)",
      "d": "√(Eρ)"
    },
    "answer": "b",
    "explanation": "v = √(E/ρ) for longitudinal waves in a solid rod, where E is Young's modulus and ρ is density. For bulk waves in an extended solid, v = √((K + 4G/3)/ρ)."
  },
  {
    "id": 293,
    "topic": "Surface Tension – Rain Drops",
    "question": "Raindrops are spherical due to:",
    "options": {
      "a": "Gravity",
      "b": "Air resistance",
      "c": "Surface tension minimizing surface area",
      "d": "Temperature effects"
    },
    "answer": "c",
    "explanation": "Surface tension acts to minimize the surface area of a liquid for a given volume. A sphere has the minimum surface area for a given volume, so free liquid droplets form spheres."
  },
  {
    "id": 294,
    "topic": "Thermodynamics – Gay-Lussac's Law",
    "question": "If temperature of a fixed volume of gas is doubled (in Kelvin), its pressure:",
    "options": {
      "a": "Halves",
      "b": "Doubles",
      "c": "Quadruples",
      "d": "Remains constant"
    },
    "answer": "b",
    "explanation": "Gay-Lussac's Law: P/T = constant (at constant V). Doubling T doubles P: P₂ = P₁ × (T₂/T₁) = P₁ × 2."
  },
  {
    "id": 295,
    "topic": "Elasticity – Stress Concentration",
    "question": "Stress concentration occurs near:",
    "options": {
      "a": "Smooth surfaces",
      "b": "Sharp notches, holes, or discontinuities",
      "c": "Regions of uniform cross-section",
      "d": "Highly compressed regions"
    },
    "answer": "b",
    "explanation": "Stress concentration occurs at geometric discontinuities (holes, notches, fillets, cracks). The local stress can be many times the average stress. This is why notches cause premature failure."
  },
  {
    "id": 296,
    "topic": "Thermodynamics – Humidity",
    "question": "Relative humidity is defined as:",
    "options": {
      "a": "Actual vapor pressure / Saturation vapor pressure × 100%",
      "b": "Mass of water vapor / Mass of dry air",
      "c": "Dew point / Ambient temperature × 100%",
      "d": "Actual temperature / Wet bulb temperature × 100%"
    },
    "answer": "a",
    "explanation": "Relative humidity RH = (actual vapor pressure / saturation vapor pressure at same T) × 100%. RH = 100% means air is fully saturated (dew point reached)."
  },
  {
    "id": 297,
    "topic": "Waves – Seismic Waves",
    "question": "P-waves (primary seismic waves) are:",
    "options": {
      "a": "Transverse waves that cannot travel through liquid",
      "b": "Longitudinal waves that travel through solids and liquids",
      "c": "Surface waves only",
      "d": "Electromagnetic waves"
    },
    "answer": "b",
    "explanation": "P-waves (pressure/compressional waves) are longitudinal and can travel through all media (solids, liquids, gases). S-waves are transverse and cannot travel through liquids."
  },
  {
    "id": 298,
    "topic": "Thermodynamics – Dew Point",
    "question": "The dew point is the temperature at which:",
    "options": {
      "a": "Water starts boiling",
      "b": "Air becomes saturated and condensation begins",
      "c": "Ice starts forming in the atmosphere",
      "d": "Relative humidity reaches 50%"
    },
    "answer": "b",
    "explanation": "Dew point is the temperature to which air must be cooled (at constant pressure) for water vapor to condense. At dew point, RH = 100%."
  },
  {
    "id": 299,
    "topic": "Fluid Mechanics – Flow Rate",
    "question": "A pipe discharges 0.6 m³ of water per minute. The volumetric flow rate in m³/s is:",
    "options": {
      "a": "0.1 m³/s",
      "b": "0.01 m³/s",
      "c": "36 m³/s",
      "d": "6 m³/s"
    },
    "answer": "b",
    "explanation": "Q = 0.6 m³/min ÷ 60 s/min = 0.01 m³/s"
  },
  {
    "id": 300,
    "topic": "Thermodynamics – Real vs Ideal Gas",
    "question": "Real gases deviate from ideal gas behavior most significantly at:",
    "options": {
      "a": "High temperature and low pressure",
      "b": "Low temperature and high pressure",
      "c": "Standard temperature and pressure",
      "d": "Low temperature and low pressure"
    },
    "answer": "b",
    "explanation": "At low T and high P, molecules are close together and intermolecular forces become significant, causing significant deviation from PV = nRT. At high T and low P, real gases behave most ideally."
  },
  {
    "id": 301,
    "topic": "Waves – Doppler Effect Calculation",
    "question": "A source emits sound at 500 Hz and moves toward a stationary observer at 34 m/s. The observed frequency is: (v_sound = 340 m/s)",
    "options": {
      "a": "450 Hz",
      "b": "500 Hz",
      "c": "550 Hz",
      "d": "600 Hz"
    },
    "answer": "c",
    "explanation": "f' = f × v/(v − v_s) = 500 × 340/(340 − 34) = 500 × 340/306 = 500 × 1.111 ≈ 555 Hz ≈ 550 Hz"
  },
  {
    "id": 302,
    "topic": "Fluid Mechanics – Magnus Effect",
    "question": "A spinning ball curves in flight due to the:",
    "options": {
      "a": "Coanda effect",
      "b": "Magnus effect",
      "c": "Bernoulli paradox",
      "d": "Stokes effect"
    },
    "answer": "b",
    "explanation": "The Magnus effect: a spinning ball drags air around it, creating a pressure difference (Bernoulli) between top and bottom, resulting in a net force causing the ball to curve."
  },
  {
    "id": 303,
    "topic": "Elasticity – Safe Load",
    "question": "A structural bolt has tensile strength 400 MPa and factor of safety 4. The maximum working stress is:",
    "options": {
      "a": "400 MPa",
      "b": "100 MPa",
      "c": "1600 MPa",
      "d": "200 MPa"
    },
    "answer": "b",
    "explanation": "Working stress = Tensile strength / Factor of safety = 400/4 = 100 MPa"
  },
  {
    "id": 304,
    "topic": "Waves – Energy Transport",
    "question": "Waves transport:",
    "options": {
      "a": "Matter",
      "b": "Energy only",
      "c": "Both matter and energy",
      "d": "Neither matter nor energy"
    },
    "answer": "b",
    "explanation": "Mechanical waves transport energy through a medium without transporting matter. The medium particles oscillate locally but do not travel with the wave."
  },
  {
    "id": 305,
    "topic": "Thermodynamics – Boltzmann Constant",
    "question": "The Boltzmann constant k_B relates:",
    "options": {
      "a": "Pressure and volume",
      "b": "Kinetic energy of a molecule to absolute temperature",
      "c": "Molar heat capacity to temperature",
      "d": "Entropy to enthalpy"
    },
    "answer": "b",
    "explanation": "k_B = R/N_A = 1.38×10⁻²³ J/K. It relates the average translational KE per molecule (3k_BT/2) to absolute temperature T."
  },
  {
    "id": 306,
    "topic": "Fluid Mechanics – Atmospheric Layers",
    "question": "Pressure decreases with altitude in the atmosphere because:",
    "options": {
      "a": "Temperature increases with height",
      "b": "Less air column above exerts less weight",
      "c": "Wind speed increases with altitude",
      "d": "Gravity is zero at high altitude"
    },
    "answer": "b",
    "explanation": "Atmospheric pressure at any altitude equals the weight per unit area of the air column above. With increasing altitude, less air is above, so pressure decreases."
  },
  {
    "id": 307,
    "topic": "Waves – Group and Phase Velocity",
    "question": "Group velocity is the velocity of:",
    "options": {
      "a": "Individual wave crests",
      "b": "The envelope (energy) of a wave packet",
      "c": "Sound in free space",
      "d": "Light in vacuum"
    },
    "answer": "b",
    "explanation": "Phase velocity (v_p = ω/k) is the speed of individual wave crests. Group velocity (v_g = dω/dk) is the speed of the wave packet's envelope — the velocity at which energy/information travels."
  },
  {
    "id": 308,
    "topic": "Thermodynamics – Diesel Cycle",
    "question": "A diesel engine operates on the:",
    "options": {
      "a": "Otto cycle",
      "b": "Rankine cycle",
      "c": "Diesel cycle",
      "d": "Brayton cycle"
    },
    "answer": "c",
    "explanation": "Diesel engines operate on the diesel cycle (constant pressure combustion). Otto cycle (constant volume combustion) is used in petrol engines. Rankine: steam turbines. Brayton: gas turbines."
  },
  {
    "id": 309,
    "topic": "Elasticity – Types of Deformation",
    "question": "Which material property describes resistance to scratching or indentation?",
    "options": {
      "a": "Toughness",
      "b": "Hardness",
      "c": "Stiffness",
      "d": "Resilience"
    },
    "answer": "b",
    "explanation": "Hardness measures resistance to surface indentation/scratching (Mohs scale, Brinell, Rockwell, Vickers tests). Stiffness = resistance to elastic deformation. Toughness = energy absorbed before fracture."
  },
  {
    "id": 310,
    "topic": "Thermodynamics – Work-Energy",
    "question": "When a gas is compressed, work is done:",
    "options": {
      "a": "By the gas on surroundings",
      "b": "On the gas by surroundings",
      "c": "By gas on itself",
      "d": "No work is done"
    },
    "answer": "b",
    "explanation": "Compression: external agent (surroundings) does positive work ON the gas. W_on_gas > 0, so W_by_gas < 0. By First Law: ΔU = Q + W_on = Q − W_by."
  },
  {
    "id": 311,
    "topic": "Fluid Mechanics – Turbines",
    "question": "In a Pelton wheel turbine, water acts on the buckets by:",
    "options": {
      "a": "Pressure difference",
      "b": "Change of momentum (impulse)",
      "c": "Buoyant force",
      "d": "Viscous drag"
    },
    "answer": "b",
    "explanation": "Pelton wheel is an impulse turbine. High-velocity water jets hit spoon-shaped buckets, transferring momentum to the wheel. Work done = rate of change of momentum."
  },
  {
    "id": 312,
    "topic": "Waves – Electromagnetic Spectrum",
    "question": "Which of the following has the shortest wavelength?",
    "options": {
      "a": "Radio waves",
      "b": "Visible light",
      "c": "X-rays",
      "d": "Gamma rays"
    },
    "answer": "d",
    "explanation": "Gamma rays have the shortest wavelength (< 0.01 nm) and highest frequency/energy in the EM spectrum. Order (decreasing λ): radio > microwave > infrared > visible > UV > X-ray > gamma."
  },
  {
    "id": 313,
    "topic": "Thermodynamics – Refrigeration",
    "question": "In a vapour compression refrigeration system, the refrigerant absorbs heat in the:",
    "options": {
      "a": "Condenser",
      "b": "Compressor",
      "c": "Expansion valve",
      "d": "Evaporator"
    },
    "answer": "d",
    "explanation": "The refrigerant evaporates in the evaporator (low-pressure, low-temperature), absorbing heat from the refrigerated space (Q_C). It condenses in the condenser, rejecting heat to surroundings."
  },
  {
    "id": 314,
    "topic": "Fluid Mechanics – Rheology",
    "question": "A non-Newtonian fluid is one in which:",
    "options": {
      "a": "Viscosity is constant regardless of shear rate",
      "b": "Viscosity changes with shear rate",
      "c": "It has no viscosity",
      "d": "Density changes with pressure"
    },
    "answer": "b",
    "explanation": "Newtonian fluids have constant viscosity (e.g., water, air). Non-Newtonian fluids: viscosity changes with shear rate. Examples: ketchup (shear-thinning), cornstarch suspension (shear-thickening)."
  },
  {
    "id": 315,
    "topic": "Waves – Mach Number",
    "question": "A Mach number of 1 corresponds to:",
    "options": {
      "a": "Twice the speed of sound",
      "b": "Half the speed of sound",
      "c": "Exactly the speed of sound",
      "d": "The speed of light"
    },
    "answer": "c",
    "explanation": "Mach number M = v/v_sound. M = 1: speed of sound (sonic). M < 1: subsonic. M > 1: supersonic. M > 5: hypersonic."
  },
  {
    "id": 316,
    "topic": "Thermodynamics – Heat Transfer Mechanisms",
    "question": "Which mode of heat transfer can occur in a vacuum?",
    "options": {
      "a": "Conduction only",
      "b": "Convection only",
      "c": "Radiation only",
      "d": "Conduction and convection"
    },
    "answer": "c",
    "explanation": "Radiation (electromagnetic waves) is the only heat transfer mode that requires no medium. Conduction and convection both require a material medium (solid or fluid)."
  },
  {
    "id": 317,
    "topic": "Waves – Reflection and Transmission",
    "question": "When a wave travels from a denser to a rarer medium, the reflected wave undergoes:",
    "options": {
      "a": "No phase change",
      "b": "Phase change of π (180°)",
      "c": "Phase change of π/2 (90°)",
      "d": "Frequency doubling"
    },
    "answer": "a",
    "explanation": "Reflection from rarer medium (lower impedance): no phase change. Reflection from denser medium (higher impedance): phase reversal of π. This applies to both mechanical and EM waves."
  },
  {
    "id": 318,
    "topic": "Fluid Mechanics – Archimedes",
    "question": "A person weighs 600 N in air and 400 N when fully submerged in water. The buoyant force is:",
    "options": {
      "a": "200 N",
      "b": "400 N",
      "c": "600 N",
      "d": "1000 N"
    },
    "answer": "a",
    "explanation": "Buoyant force = Weight in air − Apparent weight in water = 600 − 400 = 200 N. This equals the weight of displaced water."
  },
  {
    "id": 319,
    "topic": "Thermodynamics – Polytropic",
    "question": "In an adiabatic process with γ = 1.4, if pressure doubles during compression, the volume changes by a factor of:",
    "options": {
      "a": "2",
      "b": "0.5",
      "c": "2^(1/1.4) ≈ 0.629",
      "d": "2^(-1/1.4) ≈ 0.629"
    },
    "answer": "d",
    "explanation": "PVᵞ = const → P₁V₁ᵞ = P₂V₂ᵞ → V₂/V₁ = (P₁/P₂)^(1/γ) = (1/2)^(1/1.4) = 2^(−1/1.4) ≈ 0.629"
  },
  {
    "id": 320,
    "topic": "Fluid Mechanics – Hydraulic Jump",
    "question": "A hydraulic jump occurs when:",
    "options": {
      "a": "Subcritical flow suddenly changes to supercritical",
      "b": "Supercritical flow suddenly changes to subcritical with energy loss",
      "c": "Flow velocity equals wave velocity",
      "d": "A fluid changes from laminar to turbulent"
    },
    "answer": "b",
    "explanation": "A hydraulic jump is an abrupt transition from supercritical (fast, shallow) to subcritical (slow, deep) flow, accompanied by significant energy dissipation as turbulence."
  },
  {
    "id": 321,
    "topic": "Thermodynamics – Adiabatic Lapse Rate",
    "question": "Air cools as it rises in the atmosphere due to:",
    "options": {
      "a": "Radiation losses",
      "b": "Adiabatic expansion",
      "c": "Conduction to space",
      "d": "Increased wind speed"
    },
    "answer": "b",
    "explanation": "As air rises, pressure decreases. The air expands adiabatically (no heat exchange), doing work and cooling. The dry adiabatic lapse rate ≈ 9.8°C per km."
  },
  {
    "id": 322,
    "topic": "Waves – Phase Velocity Formula",
    "question": "The phase velocity of a wave is given by:",
    "options": {
      "a": "v = fλ",
      "b": "v = ω/k",
      "c": "v = dω/dk",
      "d": "Both a and b"
    },
    "answer": "d",
    "explanation": "Phase velocity v_p = fλ = ω/k. Both expressions are equivalent (ω = 2πf, k = 2π/λ). Group velocity is v_g = dω/dk."
  },
  {
    "id": 323,
    "topic": "Thermodynamics – Gibbs Free Energy",
    "question": "A reaction is spontaneous at constant temperature and pressure when:",
    "options": {
      "a": "ΔG > 0",
      "b": "ΔG = 0",
      "c": "ΔG < 0",
      "d": "ΔS < 0"
    },
    "answer": "c",
    "explanation": "Gibbs free energy G = H − TS. ΔG = ΔH − TΔS. Spontaneous processes have ΔG < 0. ΔG = 0 at equilibrium; ΔG > 0 means non-spontaneous."
  },
  {
    "id": 324,
    "topic": "Fluid Mechanics – Wind Tunnel",
    "question": "In wind tunnel testing, the parameter that must be matched to simulate real flight conditions is:",
    "options": {
      "a": "Froude number",
      "b": "Reynolds number",
      "c": "Mach number (for incompressible) or both Re and Ma for compressible flow",
      "d": "Euler number"
    },
    "answer": "c",
    "explanation": "For dynamic similarity: incompressible low-speed tests match Reynolds number. For high-speed (compressible) flows, both Reynolds and Mach numbers must be matched."
  },
  {
    "id": 325,
    "topic": "Waves – Harmonics",
    "question": "The third harmonic of a fundamental frequency of 100 Hz is:",
    "options": {
      "a": "100 Hz",
      "b": "200 Hz",
      "c": "300 Hz",
      "d": "400 Hz"
    },
    "answer": "c",
    "explanation": "nth harmonic = n × fundamental frequency. Third harmonic = 3 × 100 = 300 Hz."
  },
  {
    "id": 326,
    "topic": "Thermodynamics – Otto Cycle",
    "question": "The thermal efficiency of an Otto cycle depends primarily on:",
    "options": {
      "a": "The type of fuel used",
      "b": "The compression ratio",
      "c": "The engine speed",
      "d": "The ambient temperature"
    },
    "answer": "b",
    "explanation": "η_Otto = 1 − 1/r^(γ−1), where r is compression ratio. Higher compression ratio → higher efficiency. Typical petrol engines: r ≈ 8–12."
  },
  {
    "id": 327,
    "topic": "Fluid Mechanics – Chezy's Formula",
    "question": "Chezy's formula for flow in open channels relates:",
    "options": {
      "a": "Velocity to pressure gradient",
      "b": "Velocity to hydraulic radius and channel slope",
      "c": "Flow rate to pipe diameter only",
      "d": "Turbulence to kinematic viscosity"
    },
    "answer": "b",
    "explanation": "V = C√(Rh·S) where C is Chezy coefficient, Rh is hydraulic radius, S is channel slope. Used for uniform flow in open channels."
  },
  {
    "id": 328,
    "topic": "Thermodynamics – Kirchhoff's Law of Radiation",
    "question": "Kirchhoff's law of thermal radiation states that a good absorber of radiation is:",
    "options": {
      "a": "A poor emitter",
      "b": "A good emitter at the same wavelength",
      "c": "Not related to emissivity",
      "d": "A good reflector"
    },
    "answer": "b",
    "explanation": "Kirchhoff's law: at thermal equilibrium, emissivity = absorptivity (α = ε) at each wavelength. A perfect absorber (black body, α = 1) is also a perfect emitter."
  },
  {
    "id": 329,
    "topic": "Waves – Ultrasonic Applications",
    "question": "Ultrasonic waves are used in SONAR to:",
    "options": {
      "a": "Detect radio signals underwater",
      "b": "Measure depth and detect underwater objects using echo timing",
      "c": "Heat seawater",
      "d": "Transmit light signals"
    },
    "answer": "b",
    "explanation": "SONAR (Sound Navigation And Ranging) uses ultrasonic pulses. Distance = v × t/2, where t is echo travel time. Used for depth finding and detecting submarines."
  },
  {
    "id": 330,
    "topic": "Fluid Mechanics – Cavitation",
    "question": "Cavitation occurs in a fluid when:",
    "options": {
      "a": "Pressure exceeds vapor pressure",
      "b": "Local pressure drops below vapor pressure causing bubble formation",
      "c": "Temperature rises above boiling point",
      "d": "Flow becomes laminar"
    },
    "answer": "b",
    "explanation": "Cavitation: when local pressure drops below vapor pressure, the liquid vaporizes forming bubbles. When bubbles collapse near surfaces they cause severe damage (ship propellers, pump impellers)."
  },
  {
    "id": 331,
    "topic": "Thermodynamics – Wien's Law",
    "question": "Wien's Displacement Law states that the peak wavelength of black body radiation:",
    "options": {
      "a": "Increases with temperature",
      "b": "Is inversely proportional to temperature",
      "c": "Is directly proportional to temperature",
      "d": "Is independent of temperature"
    },
    "answer": "b",
    "explanation": "Wien's law: λ_max × T = 2.898×10⁻³ m·K. Hotter bodies emit at shorter (bluer) wavelengths. The Sun (T ≈ 5800 K) peaks in visible light; human body (T ≈ 310 K) peaks in infrared."
  },
  {
    "id": 332,
    "topic": "Waves – Sound in Solids",
    "question": "Both transverse and longitudinal waves can propagate in:",
    "options": {
      "a": "Gases",
      "b": "Liquids",
      "c": "Solids",
      "d": "Vacuum"
    },
    "answer": "c",
    "explanation": "Solids can support both longitudinal (P) and transverse (S) mechanical waves because they resist both compression and shear. Fluids (liquids and gases) only support longitudinal waves."
  },
],
    
    
    "Physics 101":
    [
  {
    "id": 1,
    "q": "What is the object's position at 6 s? [position-time graph provided]",
    "options": [
      "a. 2 m",
      "b. 3 m",
      "c. 7 m",
      "d. 9 m"
    ],
    "answer": "d"
  },
  {
    "id": 2,
    "q": "The motion of a potter's wheel is an example of",
    "options": [
      "a. Rotational motion",
      "b. Translational motion",
      "c. Precessional motion",
      "d. Circular Motion"
    ],
    "answer": "a"
  },
  {
    "id": 3,
    "q": "Which of the following physical quantities is NOT a vector?",
    "options": [
      "a. Pressure",
      "b. Force",
      "c. Electric field intensity",
      "d. Momentum"
    ],
    "answer": "a"
  },
  {
    "id": 4,
    "q": "Which of the following physical quantities is NOT a vector? (Set 2)",
    "options": [
      "a. Velocity",
      "b. Work",
      "c. Acceleration",
      "d. Weight"
    ],
    "answer": "b"
  },
  {
    "id": 5,
    "q": "A push of 80 N moves a 5 kg block up a 30° inclined plane. The coefficient of kinetic friction is 0.25 and the length of the plane is 20 m. Compute the work done by the resultant force acting on the block.",
    "options": [
      "a. 44.18 J",
      "b. 35.82 J",
      "c. 441.8 J",
      "d. 883.6 J"
    ],
    "answer": "d"
  },
  {
    "id": 7,
    "q": "The direction of the resultant of two vectors is given by",
    "options": [
      "a. cos⁻¹(Ay + By / Ax + Bx)",
      "b. cos⁻¹(Ax + Bx / Ay + By)",
      "c. tan⁻¹(Ay + By / Ax + Bx)",
      "d. tan⁻¹(Ay − By / Ax − Bx)"
    ],
    "answer": "c"
  },
  {
    "id": 8,
    "q": "Emeka is riding the Giant Drop at Abuja. If he free falls for 2.60 seconds, what will be his final velocity and how far will he fall? (g = 9.8 m/s²)",
    "options": [
      "a. 37.8 m, 17.4 m/s",
      "b. 12.5 m, 4.8 m/s",
      "c. 33.1 m, 25.5 m/s",
      "d. 9.0 m, 2.8 m/s"
    ],
    "answer": "c"
  },
  {
    "id": 9,
    "q": "The acceleration of a moving object is equal to the:",
    "options": [
      "a. Gradient of a displacement-time graph",
      "b. Gradient of a velocity-time graph",
      "c. Area below a speed-time graph",
      "d. Area below a displacement-time graph"
    ],
    "answer": "b"
  },
  {
    "id": 10,
    "q": "Find the magnitude and angle of R = 7i − 12j",
    "options": [
      "a. 19 at 30°",
      "b. 19 at 60°",
      "c. 19 at −60°",
      "d. 14 at −60°"
    ],
    "answer": "d"
  },
  {
    "id": 11,
    "q": "What is the time taken for a wheel of diameter 1 m rotating about a fixed axis with an initial angular velocity of 2 rad/s to gain an acceleration of 3 rad/s² with a final angular velocity of 20 rad/s?",
    "options": [
      "a. 13 s",
      "b. 16 s",
      "c. 6 s",
      "d. 8.1 s"
    ],
    "answer": "c"
  },
  {
    "id": 12,
    "q": "What is the acceleration of the object between 0 s and 2 s? [velocity-time graph provided]",
    "options": [
      "a. 0 m/s²",
      "b. 1 m/s²",
      "c. 2 m/s²",
      "d. 3 m/s²"
    ],
    "answer": "c"
  },
  {
    "id": 13,
    "q": "A 4 kg ball and a 2 kg ball have their centers separated by a distance of 40 cm. What is the force of attraction between them? (G = 6.673 × 10⁻¹¹ N m² kg⁻²)",
    "options": [
      "a. 1.3 × 10⁻⁹ N",
      "b. 3.3 × 10⁻⁹ N",
      "c. 6.5 × 10⁻¹¹ N",
      "d. 3.1 × 10⁻¹¹ N"
    ],
    "answer": "b"
  },
  {
    "id": 14,
    "q": "A compact disc accelerates uniformly from rest to an angular speed of 400 rpm in 5 s. Calculate the angular acceleration.",
    "options": [
      "a. 8.58 rad/s²",
      "b. 16.72 rad/s²",
      "c. 16.4 rad/s²",
      "d. 8.36 rad/s²"
    ],
    "answer": "d"
  },
  {
    "id": 15,
    "q": "A force of 180 N is applied tangentially to a solid aluminium disk of radius 0.3 m. If the mass of the disk is 40 kg, calculate the torque exerted.",
    "options": [
      "a. 4.5 Nm",
      "b. 12 Nm",
      "c. 133 Nm",
      "d. 54 Nm"
    ],
    "answer": "d"
  },
  {
    "id": 16,
    "q": "A passenger in a lift experiences an upward normal force of 720 N. If the weight of the man is 690 N, find his acceleration.",
    "options": [
      "a. 2.43 ms⁻²",
      "b. 1.32 ms⁻²",
      "c. 0.13 ms⁻²",
      "d. 0.43 ms⁻²"
    ],
    "answer": "d"
  },
  {
    "id": 17,
    "q": "A uniform meter rule weighs 1 kg and is pivoted at the 60 cm mark. A 40 g weight is suspended from the 100 cm mark. At which mark on the ruler should a 30 g mass be placed in order to keep the ruler in equilibrium?",
    "options": [
      "a. 20 cm",
      "b. 30 cm",
      "c. 40 cm",
      "d. 50 cm",
      "e. 70 cm"
    ],
    "answer": "c"
  },
  {
    "id": 18,
    "q": "Find the magnitude of R = 10i − 10j and the angle it makes with the positive x-axis.",
    "options": [
      "a. 10√2 units, 45°",
      "b. 10 units, 45°",
      "c. 20 units, 45°",
      "d. 20√2 units, 45°"
    ],
    "answer": "a"
  },
  {
    "id": 19,
    "q": "A wheel whose rotational inertia is 10 kg·m² starts from rest and accelerates under a constant torque of 3.0 Nm for 8.0 seconds. What is the wheel's rotational kinetic energy at the end of 8 seconds?",
    "options": [
      "a. 28.8 J",
      "b. 57.6 J",
      "c. 14.4 J",
      "d. 64 J"
    ],
    "answer": "a"
  },
  {
    "id": 20,
    "q": "A hammer is placed over a block of wood of 40 mm thickness to facilitate the extraction of a nail. If a force of 100 N is required to extract the nail, find the force on the nail at the point where it starts to be removed.",
    "options": [
      "a. 500 N",
      "b. 169 N",
      "c. 100 N",
      "d. 1000 N"
    ],
    "answer": "d"
  },
  {
    "id": 21,
    "q": "Write the dimensions of a/b in the relation P = (a − t²) / bx, where P is pressure, x is distance, and t is time.",
    "options": [
      "a. M⁻¹L⁰T²",
      "b. ML⁰T²",
      "c. ML⁰T²",
      "d. MLT²"
    ],
    "answer": "b"
  },
  {
    "id": 22,
    "q": "Find the magnitude of the vector 2A + 3B, given that A = 6i + 3j − k and B = 4i − 5j + 8k.",
    "options": [
      "a. 21j − 26k",
      "b. 24i − 9j + 22k",
      "c. −24i + 9j − 22k",
      "d. 12i + 6j − 2k"
    ],
    "answer": "b"
  },
  {
    "id": 23,
    "q": "A body at rest or moving with uniform velocity will have acceleration equal to:",
    "options": [
      "a. 1",
      "b. 0",
      "c. Minimum",
      "d. Maximum"
    ],
    "answer": "b"
  },
  {
    "id": 24,
    "q": "A uniform meter rule AB is supported at its centre of gravity by a knife edge. A force of 4 N is applied at a point 20 cm from end A. Calculate the force which must be applied to end B to restore equilibrium.",
    "options": [
      "a. 2 N",
      "b. 1.5 N",
      "c. 2.4 N",
      "d. 2.5 N"
    ],
    "answer": "c"
  },
  {
    "id": 25,
    "q": "Small force implies __________ pressure.",
    "options": [
      "a. Small",
      "b. Large",
      "c. Unchanged",
      "d. Either small or large"
    ],
    "answer": "d"
  },
  {
    "id": 26,
    "q": "A player stops a football weighing 0.5 kg which comes flying towards him at 10 m/s. If the impact lasts 1/50 s and the ball bounces back at 15 m/s, what is the average force involved?",
    "options": [
      "a. 250 N",
      "b. 1250 N",
      "c. 500 N",
      "d. 625 N"
    ],
    "answer": "d"
  },
  {
    "id": 27,
    "q": "What is the acceleration due to gravity on the surface of the moon if the mass of the moon is 1/80 that of Earth and its radius is one-fourth that of Earth?",
    "options": [
      "a. 16GMe / 81Re²",
      "b. GMe / 5Re²",
      "c. GMe / Re²",
      "d. 80GMe / 16Re²"
    ],
    "answer": "b"
  },
  {
    "id": 28,
    "q": "A body moves in an x-y plane. The components of velocity are vx = 5 m/s and vy = 7 m/s. What is the magnitude and direction of the velocity?",
    "options": [
      "a. 9.6 m/s, 54.5°",
      "b. 8.4 m/s, 54.5°",
      "c. 8.6 m/s, 54.5°",
      "d. 9.6 m/s, 20.0°"
    ],
    "answer": "c"
  },
  {
    "id": 30,
    "q": "A feather is dropped on the moon from a height of 1.40 meters. The acceleration of gravity on the moon is 1.67 m/s². Calculate the time for the feather to fall to the surface of the moon.",
    "options": [
      "a. 1.3 s",
      "b. 24.9 s",
      "c. 3.0 s",
      "d. 41.5 s"
    ],
    "answer": "a"
  },
  {
    "id": 31,
    "q": "A hiker walks 53.1° north of east for 2.5 km then due east for 2.0 km. What is her total displacement from her starting point?",
    "options": [
      "a. 4.0 km, 29.7°",
      "b. 5.0 km, 61.3°",
      "c. 6.0 km, 34.9°",
      "d. 7.5 km, 41.5°"
    ],
    "answer": "a"
  },
  {
    "id": 32,
    "q": "A projectile will attain its maximum range if it is fired at an angle of:",
    "options": [
      "a. 30°",
      "b. 47°",
      "c. 90°",
      "d. 45°"
    ],
    "answer": "d"
  },
  {
    "id": 33,
    "q": "A small child stands on a spring scale and it reads 100 N (mass = 10 kg). If he stands on the scale while accelerating upward in an elevator at 2 m/s², how many Newtons would the scale exert?",
    "options": [
      "a. 120 N",
      "b. 480 N",
      "c. 600 N",
      "d. 720 N"
    ],
    "answer": "a"
  },
  {
    "id": 34,
    "q": "A force of 180 N is applied at the end of a crowbar to lift a heavy weight. If the length of the crowbar is 50 cm, what length of crowbar will be required to lift the same weight with a 150 N force?",
    "options": [
      "a. 30 cm",
      "b. 40 cm",
      "c. 50 cm",
      "d. 60 cm"
    ],
    "answer": "d"
  },
  {
    "id": 35,
    "q": "Someone riding a motorcycle travels 6 km north then 8 km east. Determine the final position of the person from the initial position.",
    "options": [
      "a. 14 km northeast",
      "b. 14 km southwest",
      "c. 10 km northeast",
      "d. 10 km northwest"
    ],
    "answer": "c"
  },
  {
    "id": 36,
    "q": "A 1 m long uniform beam of 2 kg mass is hinged at the 0 cm mark. What minimum vertical force applied at the 100 cm mark is required to lift the beam? (g = 10 m/s²)",
    "options": [
      "a. 1.0 N",
      "b. 2.0 N",
      "c. 10 N",
      "d. 20 N"
    ],
    "answer": "c"
  },
  {
    "id": 37,
    "q": "The resultant of two vectors A and B is C = 2.2i + 3.4j. If vector A = 1.5i − 2.0j, find the magnitude of B and the angle it makes with the positive x-axis.",
    "options": [
      "a. 29.70 units, 82.6°",
      "b. 29.70 units, 7.4°",
      "c. 2.45 units, 82.6°",
      "d. 5.45 units, 82.6°"
    ],
    "answer": "d"
  },
  {
    "id": 38,
    "q": "What magnitude of net force is required to give a 135 kg refrigerator an acceleration of magnitude 1.40 m/s²?",
    "options": [
      "a. 1.89 m",
      "b. 18.9 N",
      "c. 189 m",
      "d. 189 N"
    ],
    "answer": "d"
  },
  {
    "id": 39,
    "q": "A train moves at a constant velocity of 50 km/h. How far will it move in 0.5 h?",
    "options": [
      "a. 10 km",
      "b. 20 km",
      "c. 25 km",
      "d. 45 km"
    ],
    "answer": "c"
  },
  {
    "id": 40,
    "q": "The motion of a rigid body consists of:",
    "options": [
      "a. Rotational motion only",
      "b. Translational motion only",
      "c. Oscillatory motion",
      "d. Translational and Rotational motion"
    ],
    "answer": "d"
  },
  {
    "id": 41,
    "q": "A car having a mass of 1000 kg is moving at 30 m/s. Brakes are applied; the frictional force between tyres and road is 5000 N. How long will the car take to come to rest?",
    "options": [
      "a. 5 seconds",
      "b. 10 seconds",
      "c. 12 seconds",
      "d. 6 seconds"
    ],
    "answer": "d"
  },
  {
    "id": 42,
    "q": "A particle moves along the x-axis with position x(t) = 3t³ − 9t² + 5. What is the acceleration of the particle at t = 2 s?",
    "options": [
      "a. 18 m/s²",
      "b. 12 m/s²",
      "c. 6 m/s²",
      "d. 36 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 43,
    "q": "A car accelerates from 20 m/s to 50 m/s over a distance of 210 m. What is the acceleration?",
    "options": [
      "a. 3.0 m/s²",
      "b. 5.0 m/s²",
      "c. 4.0 m/s²",
      "d. 6.0 m/s²"
    ],
    "answer": "b"
  },
  {
    "id": 44,
    "q": "A stone is thrown vertically upward with a speed of 25 m/s. How high does it go before momentarily stopping? (g = 10 m/s²)",
    "options": [
      "a. 31.25 m",
      "b. 62.5 m",
      "c. 25.0 m",
      "d. 12.5 m"
    ],
    "answer": "a"
  },
  {
    "id": 45,
    "q": "Two vectors P = 3i + 4j and Q = 4i − 3j. What is the angle between them?",
    "options": [
      "a. 90°",
      "b. 45°",
      "c. 0°",
      "d. 60°"
    ],
    "answer": "a"
  },
  {
    "id": 46,
    "q": "A vector A has magnitude 10 units and makes an angle of 30° with the x-axis. What are its x and y components?",
    "options": [
      "a. 8.66, 5.0",
      "b. 5.0, 8.66",
      "c. 7.07, 7.07",
      "d. 10.0, 0.0"
    ],
    "answer": "a"
  },
  {
    "id": 47,
    "q": "A force F = (4i + 3j) N acts on a body displaced by d = (2i − j) m. What is the work done?",
    "options": [
      "a. 5 J",
      "b. 11 J",
      "c. 7 J",
      "d. 3 J"
    ],
    "answer": "a"
  },
  {
    "id": 48,
    "q": "A 10 kg object is acted upon by forces F₁ = 20i N and F₂ = −8i + 6j N. What is the magnitude of the resulting acceleration?",
    "options": [
      "a. 1.56 m/s²",
      "b. 2.0 m/s²",
      "c. 1.2 m/s²",
      "d. 2.6 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 49,
    "q": "A disk of mass 5 kg and radius 0.4 m rotates at 120 rpm. What is its angular momentum? (I = ½mr²)",
    "options": [
      "a. 1.005 kg·m²/s",
      "b. 2.01 kg·m²/s",
      "c. 0.503 kg·m²/s",
      "d. 4.02 kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 50,
    "q": "A body of mass 2 kg moves with velocity v = (3i + 4j) m/s. What is its kinetic energy?",
    "options": [
      "a. 25 J",
      "b. 50 J",
      "c. 12.5 J",
      "d. 100 J"
    ],
    "answer": "a"
  },
  {
    "id": 51,
    "q": "A projectile is launched at 30° with an initial speed of 40 m/s. What is the maximum height reached? (g = 10 m/s²)",
    "options": [
      "a. 20 m",
      "b. 40 m",
      "c. 80 m",
      "d. 10 m"
    ],
    "answer": "a"
  },
  {
    "id": 52,
    "q": "A projectile is fired at 45° with speed 20 m/s. What is its horizontal range? (g = 10 m/s²)",
    "options": [
      "a. 40 m",
      "b. 20 m",
      "c. 80 m",
      "d. 10 m"
    ],
    "answer": "a"
  },
  {
    "id": 53,
    "q": "A 3 kg block slides down a frictionless incline of angle 37°. What is its acceleration? (g = 10 m/s², sin 37° = 0.6)",
    "options": [
      "a. 6 m/s²",
      "b. 8 m/s²",
      "c. 3 m/s²",
      "d. 10 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 54,
    "q": "A 5 kg block is pulled along a horizontal surface by a force of 30 N at 30° above horizontal. If μk = 0.2 and g = 10 m/s², what is the acceleration?",
    "options": [
      "a. 3.39 m/s²",
      "b. 2.20 m/s²",
      "c. 4.50 m/s²",
      "d. 1.80 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 55,
    "q": "An object undergoes circular motion of radius 0.5 m at 4 rad/s. What is the centripetal acceleration?",
    "options": [
      "a. 8 m/s²",
      "b. 2 m/s²",
      "c. 16 m/s²",
      "d. 4 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 56,
    "q": "A 0.3 kg ball on a 0.8 m string moves in a horizontal circle at 5 m/s. What is the tension in the string?",
    "options": [
      "a. 9.375 N",
      "b. 18.75 N",
      "c. 4.69 N",
      "d. 37.5 N"
    ],
    "answer": "a"
  },
  {
    "id": 57,
    "q": "What is the gravitational potential energy of a 4 kg mass at a height of 15 m? (g = 10 m/s²)",
    "options": [
      "a. 600 J",
      "b. 300 J",
      "c. 150 J",
      "d. 1200 J"
    ],
    "answer": "a"
  },
  {
    "id": 58,
    "q": "A spring of constant k = 200 N/m is compressed by 0.1 m. What is the elastic potential energy stored?",
    "options": [
      "a. 1 J",
      "b. 2 J",
      "c. 0.5 J",
      "d. 4 J"
    ],
    "answer": "a"
  },
  {
    "id": 59,
    "q": "A 2 kg object falls freely from rest through 5 m. Using energy conservation, what is its speed just before impact? (g = 10 m/s²)",
    "options": [
      "a. 10 m/s",
      "b. 7.07 m/s",
      "c. 5 m/s",
      "d. 14.14 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 60,
    "q": "A 4 kg object moving at 6 m/s collides and sticks to a stationary 2 kg object. What is the velocity after collision?",
    "options": [
      "a. 4 m/s",
      "b. 3 m/s",
      "c. 6 m/s",
      "d. 2 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 61,
    "q": "A 3 kg ball moving at 8 m/s collides elastically head-on with a stationary 3 kg ball. What are their velocities after collision?",
    "options": [
      "a. 0 m/s and 8 m/s",
      "b. 4 m/s and 4 m/s",
      "c. 8 m/s and 0 m/s",
      "d. 2 m/s and 6 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 62,
    "q": "A solid sphere of mass 3 kg and radius 0.2 m rolls without slipping at 5 m/s. What is its total kinetic energy? (I = 2/5 mr²)",
    "options": [
      "a. 52.5 J",
      "b. 37.5 J",
      "c. 75 J",
      "d. 26.25 J"
    ],
    "answer": "a"
  },
  {
    "id": 63,
    "q": "A torque of 25 Nm acts on a flywheel with moment of inertia 5 kg·m² initially at rest. What is its angular velocity after 4 s?",
    "options": [
      "a. 20 rad/s",
      "b. 5 rad/s",
      "c. 100 rad/s",
      "d. 10 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 64,
    "q": "A rod of mass 6 kg and length 2 m rotates about one end. What is its moment of inertia? (I = ⅓ ML²)",
    "options": [
      "a. 8 kg·m²",
      "b. 4 kg·m²",
      "c. 12 kg·m²",
      "d. 2 kg·m²"
    ],
    "answer": "a"
  },
  {
    "id": 65,
    "q": "A spinning top has angular momentum L = 0.5 kg·m²/s. If a torque of 0.1 Nm acts on it for 3 s, what is the new angular momentum?",
    "options": [
      "a. 0.8 kg·m²/s",
      "b. 0.2 kg·m²/s",
      "c. 1.5 kg·m²/s",
      "d. 0.35 kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 66,
    "q": "The angular velocity of a rotating body changes from 10 rad/s to 40 rad/s in 6 s. What is the angular acceleration?",
    "options": [
      "a. 5 rad/s²",
      "b. 8.33 rad/s²",
      "c. 10 rad/s²",
      "d. 3 rad/s²"
    ],
    "answer": "a"
  },
  {
    "id": 67,
    "q": "A wheel starts from rest with angular acceleration of 2 rad/s². How many revolutions does it make in 10 s?",
    "options": [
      "a. 15.9 rev",
      "b. 31.8 rev",
      "c. 10 rev",
      "d. 5 rev"
    ],
    "answer": "a"
  },
  {
    "id": 68,
    "q": "A 1500 kg car moves at 20 m/s on a flat road with μk = 0.04. What is the friction force opposing motion? (g = 10 m/s²)",
    "options": [
      "a. 600 N",
      "b. 300 N",
      "c. 1200 N",
      "d. 150 N"
    ],
    "answer": "a"
  },
  {
    "id": 72,
    "q": "A 0.5 kg bullet traveling at 400 m/s embeds in a 10 kg wooden block at rest. What is the velocity of the block-bullet system after impact?",
    "options": [
      "a. 19.05 m/s",
      "b. 40 m/s",
      "c. 9.52 m/s",
      "d. 4.76 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 73,
    "q": "A satellite orbits Earth at a radius of 2R_E. What is its orbital speed if the orbital speed at R_E is v₀?",
    "options": [
      "a. v₀/√2",
      "b. v₀/2",
      "c. v₀√2",
      "d. 2v₀"
    ],
    "answer": "a"
  },
  {
    "id": 74,
    "q": "What is the escape velocity from a planet of mass M and radius R?",
    "options": [
      "a. √(2GM/R)",
      "b. √(GM/R)",
      "c. 2GM/R",
      "d. GM/R²"
    ],
    "answer": "a"
  },
  {
    "id": 75,
    "q": "Two masses m₁ = 3 kg and m₂ = 7 kg are on a frictionless surface connected by a rope. A force of 50 N pulls m₁. What is the tension in the rope?",
    "options": [
      "a. 35 N",
      "b. 15 N",
      "c. 50 N",
      "d. 25 N"
    ],
    "answer": "a"
  },
  {
    "id": 76,
    "q": "A ball is thrown horizontally from a cliff 45 m high at 20 m/s. How far from the base of the cliff does it land? (g = 10 m/s²)",
    "options": [
      "a. 60 m",
      "b. 30 m",
      "c. 90 m",
      "d. 45 m"
    ],
    "answer": "a"
  },
  {
    "id": 77,
    "q": "The velocity of a particle is v = (6t² − 4t) m/s. What is the displacement between t = 1 s and t = 3 s?",
    "options": [
      "a. 42 m",
      "b. 46 m",
      "c. 38 m",
      "d. 50 m"
    ],
    "answer": "b"
  },
  {
    "id": 78,
    "q": "Determine the dimensions of the universal gravitational constant G.",
    "options": [
      "a. M⁻¹L³T⁻²",
      "b. M¹L³T⁻²",
      "c. M⁻¹L²T⁻²",
      "d. M⁻²L³T⁻²"
    ],
    "answer": "a"
  },
  {
    "id": 79,
    "q": "What are the dimensions of pressure?",
    "options": [
      "a. ML⁻¹T⁻²",
      "b. MLT⁻²",
      "c. ML²T⁻²",
      "d. ML⁻²T⁻²"
    ],
    "answer": "a"
  },
  {
    "id": 80,
    "q": "If force F, length L, and time T are taken as fundamental quantities, what are the dimensions of mass?",
    "options": [
      "a. FL⁻¹T²",
      "b. FLT⁻²",
      "c. FL⁻¹T⁻²",
      "d. FLT²"
    ],
    "answer": "a"
  },
  {
    "id": 81,
    "q": "A body executes SHM with amplitude 0.5 m and frequency 2 Hz. What is the maximum acceleration?",
    "options": [
      "a. 7.90 m/s²",
      "b. 19.74 m/s²",
      "c. 39.48 m/s²",
      "d. 3.14 m/s²"
    ],
    "answer": "c"
  },
  {
    "id": 82,
    "q": "A pendulum has a period of 2 s. What is its length? (g = 9.8 m/s²)",
    "options": [
      "a. 0.993 m",
      "b. 1.96 m",
      "c. 0.5 m",
      "d. 4.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 83,
    "q": "A 2 kg block compresses a spring (k = 500 N/m) by 0.2 m. What speed does the block have when the spring returns to natural length? (frictionless)",
    "options": [
      "a. √10 m/s ≈ 3.16 m/s",
      "b. 5 m/s",
      "c. 2.5 m/s",
      "d. 10 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 84,
    "q": "A 60 kg person stands on a scale in a lift accelerating downward at 3 m/s². What does the scale read? (g = 10 m/s²)",
    "options": [
      "a. 420 N",
      "b. 600 N",
      "c. 780 N",
      "d. 180 N"
    ],
    "answer": "a"
  },
  {
    "id": 85,
    "q": "A uniform beam of length 4 m and mass 20 kg is supported at both ends. A 50 kg load is placed 1 m from the left support. What is the reaction force at the left support? (g = 10 m/s²)",
    "options": [
      "a. 475 N",
      "b. 325 N",
      "c. 700 N",
      "d. 200 N"
    ],
    "answer": "a"
  },
  {
    "id": 86,
    "q": "A force F = (2i + 3j + k) N acts at position r = (i − j + 2k) m. What is the torque τ = r × F?",
    "options": [
      "a. 7i − 3j − 5k N·m",
      "b. 5i + 3j − 7k N·m",
      "c. 7i + 3j − 5k N·m",
      "d. −7i + 3j + 5k N·m"
    ],
    "answer": "a"
  },
  {
    "id": 87,
    "q": "A disc of moment of inertia 0.4 kg·m² is rotating at 6 rad/s. A constant torque of −0.8 Nm is applied. How long does it take to stop?",
    "options": [
      "a. 3 s",
      "b. 0.53 s",
      "c. 4.8 s",
      "d. 1.5 s"
    ],
    "answer": "a"
  },
  {
    "id": 88,
    "q": "A 2 kg mass and a 3 kg mass are on opposite ends of a 1 m massless rod pivoted at its centre. How far from the pivot must a 5 kg mass be placed on the 2 kg side to achieve equilibrium?",
    "options": [
      "a. 0.1 m",
      "b. 0.5 m",
      "c. 0.2 m",
      "d. 0.3 m"
    ],
    "answer": "a"
  },
  {
    "id": 89,
    "q": "If a body's kinetic energy is increased by 44%, by what percentage is its momentum increased?",
    "options": [
      "a. 20%",
      "b. 44%",
      "c. 22%",
      "d. 10%"
    ],
    "answer": "a"
  },
  {
    "id": 90,
    "q": "Two balls of equal mass m collide elastically. Ball 1 moves at v₀ and ball 2 is at rest. Ball 1 comes to rest after collision. What is the velocity of ball 2?",
    "options": [
      "a. v₀",
      "b. 2v₀",
      "c. v₀/2",
      "d. 0"
    ],
    "answer": "a"
  },
  {
    "id": 91,
    "q": "A force of 100 N is applied at the end of a 2 m lever arm. The perpendicular distance from the pivot to the line of action is 1.5 m. What is the torque?",
    "options": [
      "a. 150 N·m",
      "b. 200 N·m",
      "c. 100 N·m",
      "d. 50 N·m"
    ],
    "answer": "a"
  },
  {
    "id": 92,
    "q": "The velocity of a car changes from 54 km/h to 90 km/h in 5 s. What distance does it cover during this time?",
    "options": [
      "a. 100 m",
      "b. 200 m",
      "c. 50 m",
      "d. 150 m"
    ],
    "answer": "a"
  },
  {
    "id": 93,
    "q": "A body of mass 5 kg moving at 10 m/s is brought to rest by a constant force in 2 s. What is the magnitude of the force?",
    "options": [
      "a. 25 N",
      "b. 50 N",
      "c. 10 N",
      "d. 100 N"
    ],
    "answer": "a"
  },
  {
    "id": 94,
    "q": "A satellite at height h above Earth's surface has an orbital period T. If the satellite moves to height 4h, what is its new period? (R_E negligible compared to h)",
    "options": [
      "a. 8T",
      "b. 2T",
      "c. 4T",
      "d. 16T"
    ],
    "answer": "a"
  },
  {
    "id": 95,
    "q": "What is the gravitational field intensity at the surface of a planet of mass 6×10²⁴ kg and radius 6.4×10⁶ m? (G = 6.67×10⁻¹¹ N·m²/kg²)",
    "options": [
      "a. 9.77 m/s²",
      "b. 3.72 m/s²",
      "c. 1.62 m/s²",
      "d. 27.0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 96,
    "q": "A 10 kg mass hangs from a rope. A second rope pulls the mass horizontally until the first rope makes 30° with vertical. What is the horizontal force applied? (g = 10 m/s²)",
    "options": [
      "a. 57.7 N",
      "b. 100 N",
      "c. 86.6 N",
      "d. 28.9 N"
    ],
    "answer": "a"
  },
  {
    "id": 97,
    "q": "A wave has frequency 50 Hz and wavelength 4 m. What is the wave speed?",
    "options": [
      "a. 200 m/s",
      "b. 12.5 m/s",
      "c. 0.08 m/s",
      "d. 54 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 98,
    "q": "Power is defined as the rate of doing work. What are its SI dimensions?",
    "options": [
      "a. ML²T⁻³",
      "b. MLT⁻²",
      "c. ML²T⁻²",
      "d. M²L²T⁻³"
    ],
    "answer": "a"
  },
  {
    "id": 99,
    "q": "A pump lifts 200 kg of water per minute to a height of 10 m. What power does it require? (g = 10 m/s²)",
    "options": [
      "a. 333 W",
      "b. 20,000 W",
      "c. 2,000 W",
      "d. 167 W"
    ],
    "answer": "a"
  },
  {
    "id": 100,
    "q": "A rotating shaft delivers 15 kW at 300 rpm. What torque does it deliver?",
    "options": [
      "a. 477 N·m",
      "b. 50 N·m",
      "c. 4770 N·m",
      "d. 159 N·m"
    ],
    "answer": "a"
  },
  {
    "id": 101,
    "q": "The position of a particle is x = 4t² − 2t + 1. What is the instantaneous velocity at t = 3 s?",
    "options": [
      "a. 22 m/s",
      "b. 8 m/s",
      "c. 10 m/s",
      "d. 34 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 102,
    "q": "A ball of mass 0.4 kg is thrown upward at 15 m/s. What impulse does gravity impart during the first 2 s? (g = 10 m/s²)",
    "options": [
      "a. −8 N·s",
      "b. 8 N·s",
      "c. −4 N·s",
      "d. 4 N·s"
    ],
    "answer": "a"
  },
  {
    "id": 103,
    "q": "Two forces of 5 N and 12 N act at right angles. What is the magnitude of their resultant?",
    "options": [
      "a. 13 N",
      "b. 7 N",
      "c. 17 N",
      "d. 8.5 N"
    ],
    "answer": "a"
  },
  {
    "id": 104,
    "q": "A 6 kg object is at rest on a surface with μs = 0.5. What minimum horizontal force is required to start moving it? (g = 10 m/s²)",
    "options": [
      "a. 30 N",
      "b. 60 N",
      "c. 15 N",
      "d. 3 N"
    ],
    "answer": "a"
  },
  {
    "id": 105,
    "q": "A 2 kg ball is swung in a vertical circle of radius 1.5 m. What is the minimum speed at the top of the circle to maintain circular motion? (g = 10 m/s²)",
    "options": [
      "a. 3.87 m/s",
      "b. 5.48 m/s",
      "c. 7.75 m/s",
      "d. 1.94 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 106,
    "q": "A hollow cylinder (I = MR²) of mass 4 kg and radius 0.3 m spins at 8 rad/s. What is its rotational kinetic energy?",
    "options": [
      "a. 11.52 J",
      "b. 5.76 J",
      "c. 23.04 J",
      "d. 2.88 J"
    ],
    "answer": "a"
  },
  {
    "id": 107,
    "q": "A uniform ladder of length 5 m and mass 20 kg leans against a frictionless wall at 60° to the horizontal. What is the normal reaction from the wall? (g = 10 m/s²)",
    "options": [
      "a. 57.7 N",
      "b. 100 N",
      "c. 28.9 N",
      "d. 115 N"
    ],
    "answer": "a"
  },
  {
    "id": 108,
    "q": "A particle starts from rest and has acceleration a = (4t − 2) m/s². What is the velocity at t = 3 s?",
    "options": [
      "a. 12 m/s",
      "b. 10 m/s",
      "c. 6 m/s",
      "d. 18 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 109,
    "q": "A 500 g ball hits a wall at 10 m/s and bounces back at 8 m/s, contact time 0.02 s. What is the average force exerted on the ball?",
    "options": [
      "a. 450 N",
      "b. 900 N",
      "c. 225 N",
      "d. 50 N"
    ],
    "answer": "a"
  },
  {
    "id": 110,
    "q": "What is the coefficient of static friction for a block on an incline if it just starts to slide at an angle of 30°? (tan 30° ≈ 0.577)",
    "options": [
      "a. 0.577",
      "b. 0.866",
      "c. 0.500",
      "d. 0.707"
    ],
    "answer": "a"
  },
  {
    "id": 111,
    "q": "The angular displacement of a wheel is θ = 5t³ − 3t². What is the angular acceleration at t = 2 s?",
    "options": [
      "a. 54 rad/s²",
      "b. 30 rad/s²",
      "c. 24 rad/s²",
      "d. 12 rad/s²"
    ],
    "answer": "a"
  },
  {
    "id": 112,
    "q": "A solid cylinder (I = ½MR²) rolls without slipping down an incline of height 2 m. What is its speed at the bottom? (g = 10 m/s²)",
    "options": [
      "a. 5.16 m/s",
      "b. 6.32 m/s",
      "c. 4.47 m/s",
      "d. 3.65 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 113,
    "q": "A particle of mass 3 kg moves in a circle of radius 2 m with angular velocity 4 rad/s. What is the magnitude of the centripetal force?",
    "options": [
      "a. 96 N",
      "b. 48 N",
      "c. 24 N",
      "d. 192 N"
    ],
    "answer": "a"
  },
  {
    "id": 114,
    "q": "A uniform rod of mass 4 kg and length 3 m is pivoted at one end and held horizontal. What torque does gravity exert about the pivot?",
    "options": [
      "a. 60 N·m",
      "b. 120 N·m",
      "c. 30 N·m",
      "d. 15 N·m"
    ],
    "answer": "a"
  },
  {
    "id": 115,
    "q": "A bullet of mass 20 g travels at 500 m/s. It embeds in a 5 kg block hanging by a string. How high does the block rise? (g = 10 m/s²)",
    "options": [
      "a. 0.098 m",
      "b. 0.196 m",
      "c. 0.049 m",
      "d. 0.392 m"
    ],
    "answer": "a"
  },
  {
    "id": 116,
    "q": "Two masses 5 kg and 3 kg are connected over a frictionless pulley (Atwood machine). What is the acceleration of the system? (g = 10 m/s²)",
    "options": [
      "a. 2.5 m/s²",
      "b. 5.0 m/s²",
      "c. 1.25 m/s²",
      "d. 10 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 117,
    "q": "A particle's velocity is described by v = 3t² − 12. At what time is the particle momentarily at rest?",
    "options": [
      "a. 2 s",
      "b. 4 s",
      "c. 3 s",
      "d. 1 s"
    ],
    "answer": "a"
  },
  {
    "id": 118,
    "q": "Find the dot product A·B if A = 2i − 3j + k and B = i + 2j − 4k.",
    "options": [
      "a. −8",
      "b. 8",
      "c. 0",
      "d. −4"
    ],
    "answer": "a"
  },
  {
    "id": 119,
    "q": "Find |A × B| if A = 3i + 2j and B = i − j. (Magnitude of cross product)",
    "options": [
      "a. 5 units",
      "b. 3 units",
      "c. 7 units",
      "d. 1 unit"
    ],
    "answer": "a"
  },
  {
    "id": 120,
    "q": "The period of a satellite orbiting Earth at radius r from the centre is T = 2π√(r³/GM). What does the period become when r is tripled?",
    "options": [
      "a. 3√3 T",
      "b. 3T",
      "c. 9T",
      "d. √3 T"
    ],
    "answer": "a"
  },
  {
    "id": 121,
    "q": "A man pulls a 20 kg box 10 m along a horizontal floor with a force of 80 N at 40° above horizontal. How much work does he do?",
    "options": [
      "a. 612.8 J",
      "b. 800 J",
      "c. 514.7 J",
      "d. 1000 J"
    ],
    "answer": "a"
  },
  {
    "id": 122,
    "q": "A 300 g mass oscillates on a spring with k = 120 N/m. What is the period of oscillation?",
    "options": [
      "a. 0.314 s",
      "b. 0.628 s",
      "c. 0.157 s",
      "d. 1.00 s"
    ],
    "answer": "a"
  },
  {
    "id": 123,
    "q": "What is the velocity at which a body must be projected horizontally from the top of a 100 m cliff to land 200 m from the base? (g = 10 m/s²)",
    "options": [
      "a. 44.7 m/s",
      "b. 22.4 m/s",
      "c. 63.2 m/s",
      "d. 14.1 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 124,
    "q": "A particle of mass 2 kg moves under F = 8i − 6j N. If it starts from rest, what is the speed after 3 s?",
    "options": [
      "a. 15 m/s",
      "b. 5 m/s",
      "c. 30 m/s",
      "d. 10 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 125,
    "q": "A 10 kg block is pushed up a 30° incline (μk = 0.3) by a horizontal force F. If the block accelerates at 2 m/s², find F. (g = 10 m/s²; sin30° = 0.5, cos30° = 0.866)",
    "options": [
      "a. 121.5 N",
      "b. 86.6 N",
      "c. 98.2 N",
      "d. 65.0 N"
    ],
    "answer": "a"
  },
  {
    "id": 127,
    "q": "A body moves with position x = A sin(ωt). What is the phase difference between its displacement and velocity?",
    "options": [
      "a. 90°",
      "b. 0°",
      "c. 180°",
      "d. 45°"
    ],
    "answer": "a"
  },
  {
    "id": 128,
    "q": "A flywheel with I = 20 kg·m² is rotating at 60 rpm. A braking torque of 10 Nm is applied. How long does it take to stop?",
    "options": [
      "a. 12.57 s",
      "b. 6.28 s",
      "c. 3.14 s",
      "d. 25.13 s"
    ],
    "answer": "a"
  },
  {
    "id": 129,
    "q": "Two vectors of magnitudes 5 and 12 have a resultant of 13. What is the angle between the two vectors?",
    "options": [
      "a. 90°",
      "b. 0°",
      "c. 180°",
      "d. 60°"
    ],
    "answer": "a"
  },
  {
    "id": 130,
    "q": "A 2 kg particle moves in a circle of radius 3 m. Its KE = 54 J. What is the centripetal force on the particle?",
    "options": [
      "a. 36 N",
      "b. 18 N",
      "c. 54 N",
      "d. 72 N"
    ],
    "answer": "a"
  },
  {
    "id": 131,
    "q": "A stone is thrown at 60° above horizontal at 30 m/s. What is the speed of the stone at the highest point? (g = 10 m/s²)",
    "options": [
      "a. 15 m/s",
      "b. 25.98 m/s",
      "c. 30 m/s",
      "d. 0 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 132,
    "q": "Using dimensional analysis, which formula for the period of a pendulum is dimensionally correct, where m is mass, L is length, and g is acceleration due to gravity?",
    "options": [
      "a. T = 2π√(L/g)",
      "b. T = 2π√(m/g)",
      "c. T = 2π√(g/L)",
      "d. T = 2π√(L·m/g)"
    ],
    "answer": "a"
  },
  {
    "id": 133,
    "q": "An object is dropped from a height and takes 4 s to reach the ground. From what height was it dropped? (g = 10 m/s²)",
    "options": [
      "a. 80 m",
      "b. 40 m",
      "c. 160 m",
      "d. 20 m"
    ],
    "answer": "a"
  },
  {
    "id": 134,
    "q": "A spring is stretched by 0.05 m when a 1 kg mass hangs from it. What is the spring constant? (g = 10 m/s²)",
    "options": [
      "a. 200 N/m",
      "b. 100 N/m",
      "c. 20 N/m",
      "d. 50 N/m"
    ],
    "answer": "a"
  },
  {
    "id": 135,
    "q": "A body of mass 3 kg has momentum 18 kg·m/s. What is its kinetic energy?",
    "options": [
      "a. 54 J",
      "b. 27 J",
      "c. 108 J",
      "d. 36 J"
    ],
    "answer": "a"
  },
  {
    "id": 136,
    "q": "A 40 kg child sits 2 m from the centre of a seesaw. Where must a 60 kg adult sit on the other side for balance?",
    "options": [
      "a. 1.33 m from centre",
      "b. 2 m from centre",
      "c. 3 m from centre",
      "d. 0.67 m from centre"
    ],
    "answer": "a"
  },
  {
    "id": 137,
    "q": "What is the work done in moving a 5 kg mass up a 4 m vertical height and 3 m horizontal distance along an incline? (g = 10 m/s²; frictionless)",
    "options": [
      "a. 200 J",
      "b. 150 J",
      "c. 250 J",
      "d. 350 J"
    ],
    "answer": "a"
  },
  {
    "id": 138,
    "q": "A car of mass 1200 kg moves around a flat circular track of radius 50 m at 20 m/s. What friction force is needed to keep it on track?",
    "options": [
      "a. 9,600 N",
      "b. 4,800 N",
      "c. 19,200 N",
      "d. 2,400 N"
    ],
    "answer": "a"
  },
  {
    "id": 139,
    "q": "In a collision, a 2 kg object moving at 4 m/s collides with a 3 kg object moving at −2 m/s (same line). They stick together. Find their common velocity.",
    "options": [
      "a. 0.4 m/s",
      "b. 2 m/s",
      "c. −0.4 m/s",
      "d. 1.6 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 140,
    "q": "The centre of mass of two masses m₁ = 4 kg at x₁ = 1 m and m₂ = 6 kg at x₂ = 5 m is at:",
    "options": [
      "a. 3.4 m",
      "b. 3.0 m",
      "c. 2.5 m",
      "d. 4.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 141,
    "q": "A 3 kg mass is tied to a 2 m string and swung in a vertical circle. What is the minimum tension in the string at the top? (g = 10 m/s²)",
    "options": [
      "a. 30 N (= weight)",
      "b. 0 N",
      "c. 60 N",
      "d. 15 N"
    ],
    "answer": "b"
  },
  {
    "id": 142,
    "q": "What is the velocity of a body at the highest point of a projectile that was launched at 45° with speed 20 m/s?",
    "options": [
      "a. 14.14 m/s",
      "b. 20 m/s",
      "c. 0 m/s",
      "d. 10 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 143,
    "q": "The ratio of angular velocities of the minute and hour hands of a clock is:",
    "options": [
      "a. 12:1",
      "b. 1:12",
      "c. 60:1",
      "d. 1:60"
    ],
    "answer": "a"
  },
  {
    "id": 144,
    "q": "A ball is dropped from the top of a 125 m building. What is its velocity just before hitting the ground? (g = 10 m/s²)",
    "options": [
      "a. 50 m/s",
      "b. 25 m/s",
      "c. 100 m/s",
      "d. 12.5 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 145,
    "q": "A force F = 6 N displaces an object by 4 m in 2 s. The power delivered is:",
    "options": [
      "a. 12 W",
      "b. 24 W",
      "c. 3 W",
      "d. 6 W"
    ],
    "answer": "a"
  },
  {
    "id": 146,
    "q": "A 5 kg body is moving at 3 m/s. After a collision with a wall it moves at 2 m/s in the opposite direction. What is the change in momentum?",
    "options": [
      "a. −25 kg·m/s",
      "b. 5 kg·m/s",
      "c. −5 kg·m/s",
      "d. 25 kg·m/s"
    ],
    "answer": "a"
  },
  {
    "id": 147,
    "q": "A rigid body has moment of inertia I = 8 kg·m² and rotates at 4 rad/s. An impulse torque brings it to rest in 2 s. What average torque was applied?",
    "options": [
      "a. −16 N·m",
      "b. 16 N·m",
      "c. −4 N·m",
      "d. 4 N·m"
    ],
    "answer": "a"
  },
  {
    "id": 148,
    "q": "The linear speed of a point on the equator of Earth (radius 6.4 × 10⁶ m, period 24 hr) is approximately:",
    "options": [
      "a. 465 m/s",
      "b. 232 m/s",
      "c. 930 m/s",
      "d. 7,900 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 149,
    "q": "If the radius of Earth were halved but its mass stayed the same, what would happen to g at the surface?",
    "options": [
      "a. g would quadruple",
      "b. g would double",
      "c. g would halve",
      "d. g would remain the same"
    ],
    "answer": "a"
  },
  {
    "id": 150,
    "q": "A car travels 40 km north, then 30 km east. What is the magnitude of the total displacement?",
    "options": [
      "a. 50 km",
      "b. 70 km",
      "c. 10 km",
      "d. 35 km"
    ],
    "answer": "a"
  },
  {
    "id": 151,
    "q": "A force of 200 N acts on a 0.5 m lever arm perpendicular to the arm. A resisting force of 400 N acts on the other arm. What is the length of the resisting arm for equilibrium?",
    "options": [
      "a. 0.25 m",
      "b. 0.5 m",
      "c. 1 m",
      "d. 0.1 m"
    ],
    "answer": "a"
  },
  {
    "id": 152,
    "q": "The dimension of impulse is:",
    "options": [
      "a. MLT⁻¹",
      "b. MLT⁻²",
      "c. ML²T⁻¹",
      "d. MLT"
    ],
    "answer": "a"
  },
  {
    "id": 153,
    "q": "A body thrown vertically up has zero velocity at the top. If air resistance is neglected, what is true about the acceleration at the top?",
    "options": [
      "a. g downward",
      "b. Zero",
      "c. g upward",
      "d. Greater than g downward"
    ],
    "answer": "a"
  },
  {
    "id": 154,
    "q": "A 0.2 kg mass attached to a spring (k = 80 N/m) is displaced 0.05 m from equilibrium and released. What is the maximum KE during oscillation?",
    "options": [
      "a. 0.1 J",
      "b. 0.2 J",
      "c. 0.05 J",
      "d. 0.4 J"
    ],
    "answer": "a"
  },
  {
    "id": 155,
    "q": "A body moves in SHM with amplitude 0.1 m and angular frequency 10 rad/s. What is the maximum speed?",
    "options": [
      "a. 1 m/s",
      "b. 0.1 m/s",
      "c. 10 m/s",
      "d. 0.01 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 156,
    "q": "Two spheres of radii r₁ = 1 m and r₂ = 2 m have the same mass. What is the ratio of their densities ρ₁/ρ₂?",
    "options": [
      "a. 8",
      "b. 4",
      "c. 2",
      "d. 0.5"
    ],
    "answer": "a"
  },
  {
    "id": 157,
    "q": "A 50 kg satellite orbits Earth at radius 2 × 10⁷ m. What is its orbital period? (g_surface = 9.8 m/s², R_E = 6.4 × 10⁶ m)",
    "options": [
      "a. ≈ 2.5 × 10⁴ s",
      "b. ≈ 5.0 × 10⁴ s",
      "c. ≈ 8.6 × 10³ s",
      "d. ≈ 1.2 × 10⁵ s"
    ],
    "answer": "a"
  },
  {
    "id": 158,
    "q": "A sphere of mass 2 kg moving at 6 m/s hits a stationary sphere of mass 4 kg elastically in one dimension. What is the velocity of the 4 kg sphere after collision?",
    "options": [
      "a. 4 m/s",
      "b. 2 m/s",
      "c. 6 m/s",
      "d. 3 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 159,
    "q": "A block of mass m is placed on a turntable at radius r from the centre. The turntable spins at angular speed ω. What minimum static friction coefficient prevents sliding?",
    "options": [
      "a. ω²r/g",
      "b. ωr/g",
      "c. ω²r²/g",
      "d. ω/r·g"
    ],
    "answer": "a"
  },
  {
    "id": 160,
    "q": "A 2 kg object is dropped from 20 m. Just before impact, what is its momentum? (g = 10 m/s²)",
    "options": [
      "a. 40 kg·m/s",
      "b. 20 kg·m/s",
      "c. 200 kg·m/s",
      "d. 80 kg·m/s"
    ],
    "answer": "a"
  },
  {
    "id": 161,
    "q": "A 3 kg mass at 2 m and a 5 kg mass at 8 m are on a rod. Where is the centre of mass from the origin?",
    "options": [
      "a. 5.75 m",
      "b. 5 m",
      "c. 4.25 m",
      "d. 6 m"
    ],
    "answer": "a"
  },
  {
    "id": 162,
    "q": "An incline of angle θ has a block in equilibrium. If θ is increased beyond the angle of friction, which quantity changes discontinuously?",
    "options": [
      "a. Friction force",
      "b. Normal force",
      "c. Weight component along incline",
      "d. Nothing changes"
    ],
    "answer": "a"
  },
  {
    "id": 163,
    "q": "A 4 kg object undergoes circular motion at 3 m/s in a 2 m radius circle. What is its angular momentum about the centre?",
    "options": [
      "a. 24 kg·m²/s",
      "b. 12 kg·m²/s",
      "c. 48 kg·m²/s",
      "d. 6 kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 164,
    "q": "A motor exerts a torque of 80 N·m at 150 rpm. What power (in W) does it deliver?",
    "options": [
      "a. 1256.6 W",
      "b. 628.3 W",
      "c. 2513.3 W",
      "d. 12,000 W"
    ],
    "answer": "a"
  },
  {
    "id": 165,
    "q": "A 2 kg object is projected with velocity 10 m/s at 30° above horizontal. At maximum height, what is the KE? (g = 10 m/s²)",
    "options": [
      "a. 75 J",
      "b. 100 J",
      "c. 50 J",
      "d. 25 J"
    ],
    "answer": "a"
  },
  {
    "id": 166,
    "q": "Which of the following is a scalar quantity?",
    "options": [
      "a. Energy",
      "b. Torque",
      "c. Velocity",
      "d. Magnetic field"
    ],
    "answer": "a"
  },
  {
    "id": 167,
    "q": "A ball is thrown at 37° above horizontal at 25 m/s. How far does it travel horizontally before hitting the ground? (sin37° = 0.6, cos37° = 0.8, g = 10 m/s²)",
    "options": [
      "a. 60 m",
      "b. 50 m",
      "c. 75 m",
      "d. 30 m"
    ],
    "answer": "a"
  },
  {
    "id": 168,
    "q": "A body has velocity v = 4i + 3j m/s. What is the unit vector in the direction of v?",
    "options": [
      "a. 0.8i + 0.6j",
      "b. 4i + 3j",
      "c. 0.6i + 0.8j",
      "d. i + j"
    ],
    "answer": "a"
  },
  {
    "id": 169,
    "q": "A disc initially spinning at 20 rad/s experiences an angular deceleration of 2 rad/s². How many radians does it rotate before stopping?",
    "options": [
      "a. 100 rad",
      "b. 200 rad",
      "c. 50 rad",
      "d. 400 rad"
    ],
    "answer": "a"
  },
  {
    "id": 170,
    "q": "A man of mass 70 kg stands at the centre of a rotating platform with I_platform = 200 kg·m² spinning at 2 rad/s. He walks to the edge (R = 2 m). What is the new angular velocity? (treat man as point mass)",
    "options": [
      "a. 1.18 rad/s",
      "b. 2 rad/s",
      "c. 0.59 rad/s",
      "d. 3.4 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 171,
    "q": "A uniform plank of mass 20 kg and length 6 m is supported at both ends. A 30 kg load is placed 2 m from the left end. What is the support force at the right end? (g = 10 m/s²)",
    "options": [
      "a. 200 N",
      "b. 100 N",
      "c. 300 N",
      "d. 250 N"
    ],
    "answer": "b"
  },
  {
    "id": 172,
    "q": "A 1 kg ball is attached to a 1 m string and swings in a vertical circle. At the bottom of the circle the tension is 15 N. What is the speed at the bottom? (g = 10 m/s²)",
    "options": [
      "a. √5 m/s ≈ 2.24 m/s",
      "b. √15 m/s ≈ 3.87 m/s",
      "c. √10 m/s ≈ 3.16 m/s",
      "d. √25 m/s = 5 m/s"
    ],
    "answer": "c"
  },
  {
    "id": 173,
    "q": "A force F = 10 N acts at an angle of 60° to a displacement of 5 m. What is the work done?",
    "options": [
      "a. 25 J",
      "b. 43.3 J",
      "c. 50 J",
      "d. 8.66 J"
    ],
    "answer": "a"
  },
  {
    "id": 174,
    "q": "An elevator of mass 800 kg moves upward at constant speed with a 100 kg passenger. What is the tension in the cable? (g = 10 m/s²)",
    "options": [
      "a. 9,000 N",
      "b. 8,000 N",
      "c. 1,000 N",
      "d. 10,000 N"
    ],
    "answer": "a"
  },
  {
    "id": 175,
    "q": "A 15 kg monkey hangs from one end of a 10 m massless horizontal bar. The bar is pivoted at the left end. A 25 kg child hangs 4 m from the pivot. Where must a 10 kg weight hang to balance? (measuring from pivot)",
    "options": [
      "a. 8.5 m",
      "b. 7.5 m",
      "c. 10 m",
      "d. 5 m"
    ],
    "answer": "a"
  },
  {
    "id": 176,
    "q": "Newton's law of gravitation gives the force between two masses. If both masses are doubled and the distance is halved, the force becomes:",
    "options": [
      "a. 16 times the original",
      "b. 4 times the original",
      "c. 8 times the original",
      "d. 2 times the original"
    ],
    "answer": "a"
  },
  {
    "id": 177,
    "q": "What is the tension in a rope supporting a 5 kg block that is accelerating upward at 3 m/s²? (g = 10 m/s²)",
    "options": [
      "a. 65 N",
      "b. 50 N",
      "c. 35 N",
      "d. 15 N"
    ],
    "answer": "a"
  },
  {
    "id": 178,
    "q": "A 2 kg object moving at 10 m/s has its speed reduced to 6 m/s by friction over 4 m. What is the coefficient of kinetic friction? (g = 10 m/s²)",
    "options": [
      "a. 0.8",
      "b. 0.4",
      "c. 0.2",
      "d. 1.6"
    ],
    "answer": "a"
  },
  {
    "id": 179,
    "q": "A particle moves in a plane with position r = (2t²)i + (3t − 1)j m. What is the magnitude of its acceleration at t = 1 s?",
    "options": [
      "a. 4 m/s²",
      "b. 3 m/s²",
      "c. 5 m/s²",
      "d. 7 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 180,
    "q": "A turntable initially at rest receives a constant torque of 5 N·m. If I = 0.5 kg·m², what is the angular velocity after 4 s?",
    "options": [
      "a. 40 rad/s",
      "b. 20 rad/s",
      "c. 10 rad/s",
      "d. 80 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 181,
    "q": "What fraction of the kinetic energy is lost in a perfectly inelastic collision between equal masses?",
    "options": [
      "a. 1/2",
      "b. 1/4",
      "c. 3/4",
      "d. All of it"
    ],
    "answer": "a"
  },
  {
    "id": 182,
    "q": "The work-energy theorem states that the net work done on an object equals:",
    "options": [
      "a. Its change in kinetic energy",
      "b. Its total mechanical energy",
      "c. Its change in potential energy",
      "d. Its total kinetic energy"
    ],
    "answer": "a"
  },
  {
    "id": 183,
    "q": "A 6 kg block rests on a 45° frictionless incline connected by a rope over a frictionless pulley to a hanging 4 kg mass. What is the acceleration? (g = 10 m/s², sin45° = cos45° = 0.707)",
    "options": [
      "a. 0.51 m/s²",
      "b. 2 m/s²",
      "c. 1 m/s²",
      "d. 3.54 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 184,
    "q": "A 1000 kg car brakes from 30 m/s to rest. The braking distance is 45 m. What was the braking force?",
    "options": [
      "a. 10,000 N",
      "b. 5,000 N",
      "c. 20,000 N",
      "d. 2,000 N"
    ],
    "answer": "a"
  },
  {
    "id": 185,
    "q": "An object moving at 12 m/s has its kinetic energy doubled. What is its new speed?",
    "options": [
      "a. 12√2 m/s ≈ 16.97 m/s",
      "b. 24 m/s",
      "c. 6√2 m/s",
      "d. 36 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 186,
    "q": "A man weighs 800 N at the Earth's surface. What is his weight at a height equal to the Earth's radius from the surface?",
    "options": [
      "a. 200 N",
      "b. 400 N",
      "c. 100 N",
      "d. 50 N"
    ],
    "answer": "a"
  },
  {
    "id": 187,
    "q": "A force of 300 N is applied to a wheel at radius 0.4 m. The wheel has I = 3 kg·m². What is the angular acceleration?",
    "options": [
      "a. 40 rad/s²",
      "b. 80 rad/s²",
      "c. 20 rad/s²",
      "d. 100 rad/s²"
    ],
    "answer": "a"
  },
  {
    "id": 188,
    "q": "For a body in uniform circular motion, which of the following remains constant?",
    "options": [
      "a. Speed",
      "b. Velocity",
      "c. Acceleration",
      "d. Linear momentum"
    ],
    "answer": "a"
  },
  {
    "id": 189,
    "q": "Two objects have the same momentum but different masses. Which has greater kinetic energy?",
    "options": [
      "a. The lighter one",
      "b. The heavier one",
      "c. They have equal KE",
      "d. Cannot determine"
    ],
    "answer": "a"
  },
  {
    "id": 190,
    "q": "A 3 kg object slides 10 m down a frictionless 30° incline. What is the work done by the normal force? (g = 10 m/s²)",
    "options": [
      "a. 0 J",
      "b. 150 J",
      "c. 259.8 J",
      "d. −150 J"
    ],
    "answer": "a"
  },
  {
    "id": 191,
    "q": "What is the magnitude of the resultant of three vectors: A = 3i, B = 4j, C = 12k?",
    "options": [
      "a. 13 units",
      "b. 19 units",
      "c. 7 units",
      "d. 25 units"
    ],
    "answer": "a"
  },
  {
    "id": 192,
    "q": "A wheel has angular velocity ω = (2t³ − 6t) rad/s. At what time is the angular acceleration zero?",
    "options": [
      "a. 1 s",
      "b. 2 s",
      "c. 3 s",
      "d. 0 s"
    ],
    "answer": "a"
  },
  {
    "id": 193,
    "q": "A block on a frictionless surface is connected to a wall by a spring (k = 400 N/m). If it oscillates with amplitude 0.1 m and mass 1 kg, what is the maximum speed?",
    "options": [
      "a. 2 m/s",
      "b. 4 m/s",
      "c. 1 m/s",
      "d. 0.5 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 194,
    "q": "The velocity of a particle is v = 2t² − 4t + 3 m/s. What is the average acceleration over the interval t = 1 s to t = 3 s?",
    "options": [
      "a. 4 m/s²",
      "b. 8 m/s²",
      "c. 2 m/s²",
      "d. 6 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 195,
    "q": "A satellite of mass 500 kg orbits at 300 km above Earth's surface (R_E = 6400 km). What is the gravitational force on the satellite? (g at 6700 km radius ≈ 8.9 m/s²)",
    "options": [
      "a. 4,450 N",
      "b. 4,900 N",
      "c. 3,920 N",
      "d. 5,200 N"
    ],
    "answer": "a"
  },
  {
    "id": 196,
    "q": "An ice skater spinning with arms extended (I₁ = 3 kg·m², ω₁ = 2 rad/s) pulls her arms in (I₂ = 1 kg·m²). What is her new angular velocity?",
    "options": [
      "a. 6 rad/s",
      "b. 2 rad/s",
      "c. 3 rad/s",
      "d. 9 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 197,
    "q": "A 5 kg block hangs from the ceiling by two strings making angles of 30° and 60° with the ceiling. What is the tension in the 30° string? (g = 10 m/s²)",
    "options": [
      "a. 25 N",
      "b. 43.3 N",
      "c. 50 N",
      "d. 12.5 N"
    ],
    "answer": "a"
  },
  {
    "id": 198,
    "q": "A uniform rod of length L and mass M is hinged at one end and held at 30° below horizontal. What torque does gravity exert about the hinge?",
    "options": [
      "a. MgL cos30°/2",
      "b. MgL sin30°/2",
      "c. MgL/2",
      "d. MgL cos30°"
    ],
    "answer": "b"
  },
  {
    "id": 199,
    "q": "A particle of mass 4 kg is at position r = (3i + 4j) m and has velocity v = (2i − j) m/s. What is its angular momentum about the origin?",
    "options": [
      "a. −11k kg·m²/s",
      "b. 11k kg·m²/s",
      "c. −22k kg·m²/s",
      "d. 22k kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 200,
    "q": "Two concurrent forces of 8 N and 6 N act on an object. The minimum possible resultant is:",
    "options": [
      "a. 2 N",
      "b. 10 N",
      "c. 14 N",
      "d. 0 N"
    ],
    "answer": "a"
  },
  {
    "id": 201,
    "q": "What is the height gained by a 2 kg ball thrown vertically upward at 20 m/s using the work-energy theorem? (g = 10 m/s²)",
    "options": [
      "a. 20 m",
      "b. 10 m",
      "c. 40 m",
      "d. 5 m"
    ],
    "answer": "a"
  },
  {
    "id": 202,
    "q": "A constant force does 100 J of work on a 4 kg body, starting from rest over 2 m. What is the speed attained?",
    "options": [
      "a. 7.07 m/s",
      "b. 5 m/s",
      "c. 10 m/s",
      "d. 25 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 203,
    "q": "A 2 kg mass and a 3 kg mass are connected by a light string over a frictionless pulley. What is the tension in the string? (g = 10 m/s²)",
    "options": [
      "a. 24 N",
      "b. 30 N",
      "c. 12 N",
      "d. 20 N"
    ],
    "answer": "a"
  },
  {
    "id": 204,
    "q": "Two forces act on a body: F₁ = 5 N at 0° and F₂ = 5 N at 120°. What is the magnitude of the resultant?",
    "options": [
      "a. 5 N",
      "b. 8.66 N",
      "c. 10 N",
      "d. 2.5 N"
    ],
    "answer": "a"
  },
  {
    "id": 205,
    "q": "A body of weight W is dragged along a rough surface at constant velocity by a force P at angle θ to the horizontal. Which expression gives the coefficient of friction μ?",
    "options": [
      "a. (P cosθ)/(W − P sinθ)",
      "b. P cosθ / W",
      "c. P sinθ / W",
      "d. P / (W cosθ)"
    ],
    "answer": "a"
  },
  {
    "id": 206,
    "q": "A 10 m long plank of mass 30 kg is supported at both ends. A person of mass 70 kg stands 3 m from the left end. What is the reaction force at the left support? (g = 10 m/s²)",
    "options": [
      "a. 640 N",
      "b. 360 N",
      "c. 700 N",
      "d. 300 N"
    ],
    "answer": "b"
  },
  {
    "id": 207,
    "q": "A ball of mass 0.2 kg is released from height 5 m. It bounces to 3.2 m. What percentage of energy is lost in the bounce? (g = 10 m/s²)",
    "options": [
      "a. 36%",
      "b. 64%",
      "c. 40%",
      "d. 28%"
    ],
    "answer": "a"
  },
  {
    "id": 208,
    "q": "A horizontal force of 50 N acts on a 10 kg block on a surface with μs = 0.6 and μk = 0.4. What is the acceleration? (g = 10 m/s²)",
    "options": [
      "a. 1 m/s²",
      "b. 5 m/s²",
      "c. 0 (block doesn't move)",
      "d. 2 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 209,
    "q": "A massless rod has 10 N at 2 m from pivot and 4 N at 5 m on the other side. Where must a 7 N force be placed on the 10 N side for equilibrium?",
    "options": [
      "a. No solution — net moment can't be zero",
      "b. 0 m",
      "c. 2/7 m",
      "d. 20/7 m ≈ 2.86 m"
    ],
    "answer": "d"
  },
  {
    "id": 210,
    "q": "A car rounds a banked curve of radius 100 m at angle θ = 10°. What is the ideal speed (no friction needed)? (g = 10 m/s², tan10° ≈ 0.176)",
    "options": [
      "a. 13.3 m/s",
      "b. 17.6 m/s",
      "c. 10 m/s",
      "d. 41.9 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 211,
    "q": "Which of the following is a conserved quantity in all collisions?",
    "options": [
      "a. Momentum",
      "b. Kinetic energy",
      "c. Both momentum and kinetic energy",
      "d. Mechanical energy"
    ],
    "answer": "a"
  },
  {
    "id": 212,
    "q": "A body undergoes rectilinear motion with velocity v = √(2x) m/s, where x is in metres. What is the acceleration?",
    "options": [
      "a. 1 m/s²",
      "b. 2 m/s²",
      "c. 0.5 m/s²",
      "d. Depends on x"
    ],
    "answer": "a"
  },
  {
    "id": 213,
    "q": "An object is projected at 60° above horizontal. What fraction of the launch speed is the speed at maximum height?",
    "options": [
      "a. 0.5",
      "b. 0.866",
      "c. 0.707",
      "d. 0.25"
    ],
    "answer": "a"
  },
  {
    "id": 215,
    "q": "A ball is dropped from a moving train at 20 m/s horizontal. To a stationary observer, how far does the ball travel horizontally before reaching the ground 5 m below? (g = 10 m/s²)",
    "options": [
      "a. 20 m",
      "b. 10 m",
      "c. 40 m",
      "d. 5 m"
    ],
    "answer": "a"
  },
  {
    "id": 216,
    "q": "What net upward force is needed to accelerate a 1200 kg elevator upward at 1.5 m/s²? (g = 10 m/s²)",
    "options": [
      "a. 13,800 N",
      "b. 12,000 N",
      "c. 1,800 N",
      "d. 10,200 N"
    ],
    "answer": "a"
  },
  {
    "id": 217,
    "q": "The efficiency of a machine is 80%. A force of 50 N is applied over 2 m to lift a 60 kg load. How high is the load lifted? (g = 10 m/s²)",
    "options": [
      "a. 0.133 m",
      "b. 0.167 m",
      "c. 0.1 m",
      "d. 0.25 m"
    ],
    "answer": "a"
  },
  {
    "id": 219,
    "q": "A 3 kg particle moves under a restoring force F = −12x N. What is the angular frequency of oscillation?",
    "options": [
      "a. 2 rad/s",
      "b. 4 rad/s",
      "c. 6 rad/s",
      "d. 12 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 220,
    "q": "A 5 kg object moving at 8 m/s east collides with a 10 kg object moving at 2 m/s west. They stick together. What is the final velocity?",
    "options": [
      "a. 4/3 m/s east",
      "b. 4/3 m/s west",
      "c. 4 m/s east",
      "d. 2 m/s east"
    ],
    "answer": "a"
  },
  {
    "id": 221,
    "q": "A 200 g mass on a 0.5 m string describes a horizontal circle at 3 rad/s. What is the period of revolution?",
    "options": [
      "a. 2.09 s",
      "b. 1.05 s",
      "c. 4.19 s",
      "d. 0.52 s"
    ],
    "answer": "a"
  },
  {
    "id": 222,
    "q": "The mechanical advantage of a first-class lever is 4. The effort arm is 0.8 m. How long is the load arm?",
    "options": [
      "a. 0.2 m",
      "b. 3.2 m",
      "c. 4 m",
      "d. 0.4 m"
    ],
    "answer": "a"
  },
  {
    "id": 223,
    "q": "A uniform solid cylinder of mass 8 kg and radius 0.5 m is initially at rest. A rope wrapped around it unwinds under a 40 N force. What is the angular acceleration? (I = ½MR²)",
    "options": [
      "a. 20 rad/s²",
      "b. 10 rad/s²",
      "c. 40 rad/s²",
      "d. 5 rad/s²"
    ],
    "answer": "a"
  },
  {
    "id": 224,
    "q": "A velocity-time graph shows a straight line from (0, 5) to (4, 25) m/s. What is the displacement during this interval?",
    "options": [
      "a. 60 m",
      "b. 80 m",
      "c. 40 m",
      "d. 100 m"
    ],
    "answer": "a"
  },
  {
    "id": 225,
    "q": "By what factor does the gravitational potential energy of a mass change if its height above Earth's surface is increased from R to 2R above the surface? (use ΔPE = mgh approximation is invalid; use exact formula)",
    "options": [
      "a. PE at 2R is 2/3 of PE at R (measured from Earth's centre)",
      "b. It doubles",
      "c. It quadruples",
      "d. It increases by 50%"
    ],
    "answer": "d"
  },
  {
    "id": 226,
    "q": "A particle is moving in a circle of radius 2 m. Its speed increases from 2 m/s to 4 m/s in 2 s uniformly. What is the magnitude of total acceleration at the instant when v = 3 m/s?",
    "options": [
      "a. √(1 + 20.25) ≈ 4.6 m/s²",
      "b. 4.5 m/s²",
      "c. 1 m/s²",
      "d. √(1 + 9) ≈ 3.16 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 227,
    "q": "A block of mass m₁ = 4 kg sits on top of a block of mass m₂ = 6 kg on a frictionless surface. Friction between blocks is μ = 0.3. A horizontal force F = 20 N is applied to m₂. What is the acceleration of the system? (g = 10 m/s²)",
    "options": [
      "a. 2 m/s²",
      "b. 3.33 m/s²",
      "c. 1.2 m/s²",
      "d. 5 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 228,
    "q": "A 2 kg disk (I = ½MR², R = 0.3 m) rolling without slipping at v = 4 m/s. What is the total mechanical energy?",
    "options": [
      "a. 24 J",
      "b. 16 J",
      "c. 8 J",
      "d. 32 J"
    ],
    "answer": "a"
  },
  {
    "id": 229,
    "q": "An object undergoes projectile motion. Which component of velocity remains constant throughout?",
    "options": [
      "a. Horizontal",
      "b. Vertical",
      "c. Both",
      "d. Neither"
    ],
    "answer": "a"
  },
  {
    "id": 230,
    "q": "A 10 kg block on a rough surface (μk = 0.25) is pushed by a 60 N force at 20° below horizontal. What is the acceleration? (g = 10 m/s², cos20° ≈ 0.94, sin20° ≈ 0.34)",
    "options": [
      "a. 2.29 m/s²",
      "b. 3.5 m/s²",
      "c. 1.5 m/s²",
      "d. 4.0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 232,
    "q": "A pendulum bob of mass 0.5 kg hangs on a 2 m string. It is displaced 0.2 m horizontally from equilibrium. What is the restoring force for small angles? (g = 10 m/s²)",
    "options": [
      "a. 0.5 N",
      "b. 1.0 N",
      "c. 2.0 N",
      "d. 0.25 N"
    ],
    "answer": "a"
  },
  {
    "id": 233,
    "q": "A disk (I = ½MR²) and a ring (I = MR²) of equal mass M and radius R start from rest and roll down the same incline. Which reaches the bottom first?",
    "options": [
      "a. The disk",
      "b. The ring",
      "c. They arrive simultaneously",
      "d. Depends on the incline angle"
    ],
    "answer": "a"
  },
  {
    "id": 234,
    "q": "A body of mass 5 kg moves under F = (10i + 20j) N from r₁ = (1i + 2j) m to r₂ = (3i + 4j) m. What is the work done?",
    "options": [
      "a. 60 J",
      "b. 40 J",
      "c. 80 J",
      "d. 100 J"
    ],
    "answer": "a"
  },
  {
    "id": 235,
    "q": "The moment of inertia of a solid sphere about a diameter is I = 2/5 MR². What is its moment of inertia about a tangential axis parallel to the diameter? (parallel axis theorem)",
    "options": [
      "a. 7/5 MR²",
      "b. 2/5 MR²",
      "c. 3/5 MR²",
      "d. 12/5 MR²"
    ],
    "answer": "a"
  },
  {
    "id": 236,
    "q": "A body of mass 2 kg is dropped from rest and observed to have velocity 10 m/s just before impact. What height was it dropped from? (g = 10 m/s²)",
    "options": [
      "a. 5 m",
      "b. 10 m",
      "c. 2 m",
      "d. 20 m"
    ],
    "answer": "a"
  },
  {
    "id": 237,
    "q": "A 3 kg object is subjected to two perpendicular forces: 12 N and 16 N. What is the magnitude of the resultant acceleration?",
    "options": [
      "a. 6.67 m/s²",
      "b. 9.33 m/s²",
      "c. 4 m/s²",
      "d. 12 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 238,
    "q": "Two bodies of masses 2 kg and 3 kg moving in the same direction at 6 m/s and 4 m/s respectively. They collide and the 2 kg body moves at 3 m/s after collision. What is the velocity of the 3 kg body?",
    "options": [
      "a. 5.33 m/s",
      "b. 4.67 m/s",
      "c. 6 m/s",
      "d. 2 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 239,
    "q": "A wheel of moment of inertia I = 6 kg·m² has angular kinetic energy of 75 J. What is its angular velocity?",
    "options": [
      "a. 5 rad/s",
      "b. 25 rad/s",
      "c. 2.5 rad/s",
      "d. 12.5 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 240,
    "q": "A particle has position x = 5 sin(2πt) metres. What is the maximum acceleration?",
    "options": [
      "a. 20π² m/s²",
      "b. 10π m/s²",
      "c. 5 m/s²",
      "d. 40π m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 241,
    "q": "A force F acts on a body for time t and produces a change in momentum Δp. If the same force acts for time 3t/2, the new change in momentum is:",
    "options": [
      "a. 3Δp/2",
      "b. 3Δp",
      "c. 2Δp/3",
      "d. Δp"
    ],
    "answer": "a"
  },
  {
    "id": 242,
    "q": "A particle moves along the x-axis such that x = t³ − 6t² + 9t + 2 m. At what time(s) is the particle momentarily at rest?",
    "options": [
      "a. t = 1 s and t = 3 s",
      "b. t = 2 s only",
      "c. t = 0 s and t = 2 s",
      "d. t = 3 s only"
    ],
    "answer": "a"
  },
  {
    "id": 243,
    "q": "A particle's position is x = 2t³ − 3t² m. What is the distance (not displacement) travelled between t = 0 and t = 2 s?",
    "options": [
      "a. 4 m",
      "b. 2 m",
      "c. 5 m",
      "d. 3 m"
    ],
    "answer": "c"
  },
  {
    "id": 244,
    "q": "A ball is thrown vertically upward at 30 m/s from the top of a 25 m building. What is its speed when it hits the ground? (g = 10 m/s²)",
    "options": [
      "a. 40 m/s",
      "b. 35 m/s",
      "c. 30 m/s",
      "d. 45 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 245,
    "q": "Two trains A and B move toward each other on parallel tracks. Train A is 100 m long travelling at 20 m/s; train B is 150 m long travelling at 30 m/s. How long does it take from the moment their fronts meet to the moment their rears pass?",
    "options": [
      "a. 5 s",
      "b. 7 s",
      "c. 3 s",
      "d. 10 s"
    ],
    "answer": "a"
  },
  {
    "id": 246,
    "q": "A stone is dropped into a well. The sound of the splash is heard 3.5 s later. If the speed of sound is 340 m/s, how deep is the well? (g = 10 m/s²)",
    "options": [
      "a. ≈ 52.4 m",
      "b. ≈ 61.3 m",
      "c. ≈ 45.0 m",
      "d. ≈ 70.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 247,
    "q": "A particle has velocity v = (3t² − 4)i + 2tj m/s. What is the magnitude of its acceleration at t = 2 s?",
    "options": [
      "a. √(148) ≈ 12.17 m/s²",
      "b. 12 m/s²",
      "c. 14 m/s²",
      "d. 2 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 248,
    "q": "A 5 kg block is on a rough surface (μk = 0.3). A force of 40 N at 37° above horizontal is applied. What is the normal force? (g = 10 m/s², sin37° = 0.6)",
    "options": [
      "a. 26 N",
      "b. 50 N",
      "c. 30 N",
      "d. 38 N"
    ],
    "answer": "a"
  },
  {
    "id": 249,
    "q": "Two blocks of mass 3 kg and 5 kg are in contact on a frictionless surface. A 40 N force pushes the 3 kg block. What force does the 3 kg block exert on the 5 kg block?",
    "options": [
      "a. 25 N",
      "b. 15 N",
      "c. 40 N",
      "d. 8 N"
    ],
    "answer": "a"
  },
  {
    "id": 250,
    "q": "A car of mass 1500 kg starts from rest and reaches 30 m/s in 10 s on a flat road with friction force 1000 N. What is the engine force?",
    "options": [
      "a. 5500 N",
      "b. 4500 N",
      "c. 1000 N",
      "d. 3500 N"
    ],
    "answer": "a"
  },
  {
    "id": 251,
    "q": "A 2 kg mass is tied to a 1.5 m rope and whirled in a vertical circle. The speed at the top is 4 m/s. What is the tension at the top? (g = 10 m/s²)",
    "options": [
      "a. 1.33 N",
      "b. 20 N",
      "c. 21.33 N",
      "d. 0 N"
    ],
    "answer": "a"
  },
  {
    "id": 252,
    "q": "A conical pendulum has a string of length 0.5 m and makes a half-angle of 30° with the vertical. What is the period of revolution? (g = 10 m/s², cos30° = 0.866)",
    "options": [
      "a. 1.31 s",
      "b. 0.66 s",
      "c. 2.62 s",
      "d. 0.93 s"
    ],
    "answer": "a"
  },
  {
    "id": 253,
    "q": "A 4 kg block moves along a rough surface (μk = 0.4) and compresses a spring (k = 800 N/m) by 0.15 m before stopping. What was the initial speed? (g = 10 m/s²)",
    "options": [
      "a. 3.0 m/s",
      "b. 4.24 m/s",
      "c. 2.12 m/s",
      "d. 6.0 m/s"
    ],
    "answer": "c"
  },
  {
    "id": 254,
    "q": "A pendulum of mass 0.3 kg and length 2 m is pulled 10° from vertical. What is the speed at the lowest point? (g = 10 m/s², cos10° ≈ 0.985)",
    "options": [
      "a. 0.548 m/s",
      "b. 1.095 m/s",
      "c. 0.275 m/s",
      "d. 0.774 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 255,
    "q": "A 3 kg object slides 5 m down an incline of 37° with μk = 0.2. What is its speed at the bottom starting from rest? (g = 10 m/s², sin37° = 0.6, cos37° = 0.8)",
    "options": [
      "a. 6.0 m/s",
      "b. 7.75 m/s",
      "c. 4.47 m/s",
      "d. 5.48 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 256,
    "q": "Two equal masses m = 2 kg are on either side of a frictionless pulley on an incline of angle 30°. One mass is on the incline, the other hangs freely. The system accelerates. What is the acceleration? (g = 10 m/s²)",
    "options": [
      "a. 2.5 m/s²",
      "b. 5 m/s²",
      "c. 1.25 m/s²",
      "d. 0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 257,
    "q": "A 10 kg ladder of length 5 m leans against a smooth wall at 60° to the horizontal. A 70 kg person stands 2 m up the ladder. What is the friction force at the floor? (g = 10 m/s²)",
    "options": [
      "a. 248 N",
      "b. 124 N",
      "c. 496 N",
      "d. 62 N"
    ],
    "answer": "a"
  },
  {
    "id": 258,
    "q": "The position vector of a particle is r = (2t)i + (t² − 4)j m. What is the angle the velocity vector makes with the x-axis at t = 2 s?",
    "options": [
      "a. 45°",
      "b. 63.4°",
      "c. 26.6°",
      "d. 90°"
    ],
    "answer": "a"
  },
  {
    "id": 259,
    "q": "A projectile is launched from ground level. It travels 120 m horizontally and lands at the same height in 4 s. What was the launch angle? (g = 10 m/s²)",
    "options": [
      "a. 53.1°",
      "b. 36.9°",
      "c. 45°",
      "d. 60°"
    ],
    "answer": "a"
  },
  {
    "id": 260,
    "q": "A bullet of mass 10 g is fired at 400 m/s into a 2 kg block on a frictionless surface. The bullet passes through and exits at 100 m/s. What is the block's velocity?",
    "options": [
      "a. 1.5 m/s",
      "b. 3.0 m/s",
      "c. 0.75 m/s",
      "d. 2.0 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 261,
    "q": "A 6 kg disc (I = ½MR², R = 0.4 m) is spinning at ω₀ = 10 rad/s. A braking force of 12 N is applied tangentially at the rim. How long to stop?",
    "options": [
      "a. 1.0 s",
      "b. 2.0 s",
      "c. 0.5 s",
      "d. 4.0 s"
    ],
    "answer": "a"
  },
  {
    "id": 262,
    "q": "A solid sphere (I = 2/5 MR²) rolls without slipping up an incline of 20° and travels 3 m along the slope before stopping. What was the initial speed? (g = 10 m/s², sin20° ≈ 0.342)",
    "options": [
      "a. 4.91 m/s",
      "b. 3.46 m/s",
      "c. 6.00 m/s",
      "d. 2.45 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 263,
    "q": "An object of mass m is on a frictionless surface and attached to a spring of constant k. It is given a speed v₀. What is the maximum compression of the spring?",
    "options": [
      "a. v₀√(m/k)",
      "b. v₀√(k/m)",
      "c. mv₀/k",
      "d. kv₀/m"
    ],
    "answer": "a"
  },
  {
    "id": 264,
    "q": "A uniform rod of mass 3 kg and length 1.2 m is pivoted at one end. A force of 20 N perpendicular to the rod is applied at the free end. What is the angular acceleration?",
    "options": [
      "a. 16.67 rad/s²",
      "b. 8.33 rad/s²",
      "c. 33.33 rad/s²",
      "d. 5.56 rad/s²"
    ],
    "answer": "a"
  },
  {
    "id": 265,
    "q": "A 1 kg mass oscillates on a spring with amplitude 0.2 m and angular frequency ω = 5 rad/s. At x = 0.1 m from equilibrium, what is the speed?",
    "options": [
      "a. √3 ≈ 0.866 m/s",
      "b. 1.0 m/s",
      "c. 0.5 m/s",
      "d. √5 ≈ 1.118 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 266,
    "q": "What is the period of a body performing SHM if its acceleration is 4 m/s² when displaced 0.01 m from equilibrium?",
    "options": [
      "a. π/10 s ≈ 0.314 s",
      "b. π/5 s ≈ 0.628 s",
      "c. 0.1 s",
      "d. 1.0 s"
    ],
    "answer": "a"
  },
  {
    "id": 267,
    "q": "A solid cylinder of mass 4 kg and radius 0.2 m is released from rest at the top of an incline of height 1.8 m. What is its speed at the bottom? (g = 10 m/s²)",
    "options": [
      "a. 4.90 m/s",
      "b. 6.00 m/s",
      "c. 3.46 m/s",
      "d. 5.66 m/s"
    ],
    "answer": "b"
  },
  {
    "id": 268,
    "q": "A mass m₁ = 4 kg on a frictionless horizontal surface is connected via a string over a frictionless pulley to a mass m₂ = 6 kg hanging vertically. What is the tension in the string? (g = 10 m/s²)",
    "options": [
      "a. 24 N",
      "b. 40 N",
      "c. 60 N",
      "d. 16 N"
    ],
    "answer": "a"
  },
  {
    "id": 269,
    "q": "A 0.5 kg ball is attached to a 0.8 m string. It rotates in a horizontal circle such that the string makes 60° with the vertical. What is the speed of the ball? (g = 10 m/s², tan60° ≈ 1.732, sin60° ≈ 0.866)",
    "options": [
      "a. 3.29 m/s",
      "b. 2.45 m/s",
      "c. 4.65 m/s",
      "d. 1.64 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 270,
    "q": "A 5 kg mass has position r = (3t²)i + (2t³ − t)j m. What is the magnitude of the net force on the mass at t = 1 s?",
    "options": [
      "a. √(900 + 3600) ≈ 67.1 N",
      "b. 30 N",
      "c. 60 N",
      "d. √(30² + 50²) ≈ 58.3 N"
    ],
    "answer": "d"
  },
  {
    "id": 271,
    "q": "A 2 kg block is pushed up a rough 45° incline (μk = 0.3) by a force of 30 N parallel to the incline. What is the acceleration? (g = 10 m/s², sin45° = cos45° = 0.707)",
    "options": [
      "a. 1.07 m/s²",
      "b. 3.54 m/s²",
      "c. 5.0 m/s²",
      "d. 0.71 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 272,
    "q": "A particle moves in a circle of radius R. Its speed increases uniformly from u to v in one complete revolution. What is the average tangential acceleration?",
    "options": [
      "a. (v² − u²)/(4πR)",
      "b. (v − u)/(2πR/v)",
      "c. (v² − u²)/(2πR)",
      "d. (v − u)·v/(2πR)"
    ],
    "answer": "a"
  },
  {
    "id": 273,
    "q": "A 0.4 kg ball is dropped from 5 m, hits the floor, and bounces to 3.6 m. What is the coefficient of restitution?",
    "options": [
      "a. 0.849",
      "b. 0.72",
      "c. 0.6",
      "d. 0.9"
    ],
    "answer": "a"
  },
  {
    "id": 274,
    "q": "Two identical masses m are connected by a light rod of negligible mass. One mass is at (0,0) and the other at (4,3) m. Where is the centre of mass?",
    "options": [
      "a. (2, 1.5) m",
      "b. (4, 3) m",
      "c. (1, 0.75) m",
      "d. (0, 0) m"
    ],
    "answer": "a"
  },
  {
    "id": 275,
    "q": "A 4 kg and a 6 kg mass hang on either side of a pulley with a 1 kg pulley (I = ½MR², R = 0.1 m). What is the acceleration of the system? (g = 10 m/s²)",
    "options": [
      "a. 1.82 m/s²",
      "b. 2.0 m/s²",
      "c. 4.0 m/s²",
      "d. 1.0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 276,
    "q": "A 2000 kg car travels over a circular hill of radius 30 m at 15 m/s. What is the normal force on the car at the top? (g = 10 m/s²)",
    "options": [
      "a. 5000 N",
      "b. 10,000 N",
      "c. 15,000 N",
      "d. 20,000 N"
    ],
    "answer": "a"
  },
  {
    "id": 277,
    "q": "A spring with k = 500 N/m is compressed by 0.3 m and launches a 0.5 kg ball vertically. Ignoring friction, what maximum height does the ball reach? (g = 10 m/s²)",
    "options": [
      "a. 4.5 m",
      "b. 9.0 m",
      "c. 2.25 m",
      "d. 13.5 m"
    ],
    "answer": "a"
  },
  {
    "id": 279,
    "q": "A block of mass 3 kg compresses a spring (k = 600 N/m) by 0.1 m and is released on a horizontal surface with μk = 0.25. How far does it travel before stopping? (g = 10 m/s²)",
    "options": [
      "a. 0.4 m",
      "b. 0.8 m",
      "c. 1.2 m",
      "d. 0.2 m"
    ],
    "answer": "a"
  },
  {
    "id": 280,
    "q": "Three equal masses m = 2 kg are placed at the vertices of an equilateral triangle of side 1 m. How far is the centre of mass from each vertex?",
    "options": [
      "a. 0.577 m",
      "b. 0.5 m",
      "c. 1.0 m",
      "d. 0.289 m"
    ],
    "answer": "a"
  },
  {
    "id": 281,
    "q": "A thin rod of mass M and length L is struck at one end perpendicular to its length while it is free in space. Where is the instantaneous centre of rotation?",
    "options": [
      "a. 2L/3 from struck end",
      "b. L/2 from struck end",
      "c. L/3 from struck end",
      "d. At the struck end"
    ],
    "answer": "a"
  },
  {
    "id": 282,
    "q": "A 5 kg body explodes into two parts. Part A (3 kg) moves at 4 m/s east. What is the velocity of part B (2 kg)?",
    "options": [
      "a. 6 m/s west",
      "b. 4 m/s west",
      "c. 10 m/s west",
      "d. 3 m/s west"
    ],
    "answer": "a"
  },
  {
    "id": 283,
    "q": "A 10 kg block slides down a frictionless incline and collides with a stationary 5 kg block at the bottom. The collision is perfectly inelastic. The blocks travel 2 m before stopping (μk = 0.4 on flat). What was the speed at the bottom of the incline? (g = 10 m/s²)",
    "options": [
      "a. 4.9 m/s",
      "b. 3.27 m/s",
      "c. 6.53 m/s",
      "d. 9.8 m/s"
    ],
    "answer": "c"
  },
  {
    "id": 284,
    "q": "A rocket initially at rest in free space ejects mass at rate dm/dt = 5 kg/s at exhaust velocity 300 m/s. What is the thrust force?",
    "options": [
      "a. 1500 N",
      "b. 300 N",
      "c. 60 N",
      "d. 1000 N"
    ],
    "answer": "a"
  },
  {
    "id": 286,
    "q": "A 1 kg particle undergoes SHM: x = 0.05 cos(10t) m. What is the total mechanical energy of the oscillation?",
    "options": [
      "a. 0.125 J",
      "b. 0.25 J",
      "c. 0.0625 J",
      "d. 0.5 J"
    ],
    "answer": "a"
  },
  {
    "id": 287,
    "q": "A body moves in SHM with time period 0.4 s and amplitude 0.1 m. What is the acceleration when displacement is 0.06 m?",
    "options": [
      "a. −14.8 m/s²",
      "b. 14.8 m/s²",
      "c. −9.87 m/s²",
      "d. 29.6 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 288,
    "q": "Two pendulums have lengths in the ratio 4:1. What is the ratio of their periods?",
    "options": [
      "a. 2:1",
      "b. 4:1",
      "c. 1:2",
      "d. 1:4"
    ],
    "answer": "a"
  },
  {
    "id": 289,
    "q": "A 10 kg block on a frictionless incline of 30° is connected by a rope over a frictionless pulley to a hanging 5 kg mass. What is the acceleration? (g = 10 m/s²)",
    "options": [
      "a. 0 m/s²",
      "b. 3.33 m/s²",
      "c. 1.67 m/s²",
      "d. 5.0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 290,
    "q": "The speed of a planet in an elliptical orbit is greatest at:",
    "options": [
      "a. Perihelion (closest approach to the Sun)",
      "b. Aphelion (farthest from the Sun)",
      "c. The semi-major axis endpoint",
      "d. The semi-minor axis endpoint"
    ],
    "answer": "a"
  },
  {
    "id": 291,
    "q": "A geostationary satellite is at radius r_g from Earth's centre. If a second satellite orbits at r = r_g/4, what is its orbital period? (T_g = 24 hr)",
    "options": [
      "a. 3 hr",
      "b. 6 hr",
      "c. 12 hr",
      "d. 1 hr"
    ],
    "answer": "a"
  },
  {
    "id": 292,
    "q": "The potential energy due to gravity between two masses M and m separated by r is U = −GMm/r. What does the negative sign imply?",
    "options": [
      "a. The system is bound; work must be done to separate the masses",
      "b. Gravity acts downward",
      "c. Energy is lost in the gravitational field",
      "d. The force is repulsive"
    ],
    "answer": "a"
  },
  {
    "id": 293,
    "q": "A mass m = 0.2 kg is tied to a 1 m string and swings in a vertical circle. At the bottom, the tension is 4 N. What is the speed at the bottom? (g = 10 m/s²)",
    "options": [
      "a. √10 ≈ 3.16 m/s",
      "b. 2 m/s",
      "c. 4 m/s",
      "d. √20 ≈ 4.47 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 294,
    "q": "A wheel of radius 0.5 m rolls without slipping on a flat surface at 4 m/s. What is the speed of the point at the top of the wheel?",
    "options": [
      "a. 8 m/s",
      "b. 4 m/s",
      "c. 0 m/s",
      "d. 2 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 295,
    "q": "A 4 kg uniform rod of length 2 m rotates about its centre. A 2 kg mass is attached at each end. What is the total moment of inertia? (I_rod_centre = ML²/12)",
    "options": [
      "a. 9.33 kg·m²",
      "b. 5.33 kg·m²",
      "c. 4.0 kg·m²",
      "d. 16 kg·m²"
    ],
    "answer": "a"
  },
  {
    "id": 296,
    "q": "Two forces of equal magnitude F act on a body at an angle of 120° to each other. What is the magnitude of the resultant?",
    "options": [
      "a. F",
      "b. F√3",
      "c. 2F",
      "d. F/2"
    ],
    "answer": "a"
  },
  {
    "id": 297,
    "q": "A 10 kg object is lifted by a pulley system with mechanical advantage 4. What effort is needed? (g = 10 m/s², ignore pulley mass)",
    "options": [
      "a. 25 N",
      "b. 100 N",
      "c. 40 N",
      "d. 10 N"
    ],
    "answer": "a"
  },
  {
    "id": 298,
    "q": "An object is projected at 60° from the horizontal with speed u. Find the ratio of maximum height to range.",
    "options": [
      "a. tan60°/4 = √3/4 ≈ 0.433",
      "b. tan60°/2 = √3/2",
      "c. 2/tan60°",
      "d. 1/4"
    ],
    "answer": "a"
  },
  {
    "id": 299,
    "q": "A 3 kg block is placed on a 5 kg block which sits on a frictionless surface. μ between blocks = 0.4. A 30 N force is applied to the top block. Find the acceleration of the bottom block. (g = 10 m/s²)",
    "options": [
      "a. 2.4 m/s²",
      "b. 4.0 m/s²",
      "c. 0 m/s²",
      "d. 6.0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 300,
    "q": "A ball of mass 2 kg moving at 5 m/s collides elastically with a ball of mass 6 kg at rest. What is the velocity of the 2 kg ball after collision?",
    "options": [
      "a. −2.5 m/s",
      "b. 2.5 m/s",
      "c. −5.0 m/s",
      "d. 1.25 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 301,
    "q": "A 2 kg mass oscillates on a spring (k = 50 N/m). At t = 0, x = 0.1 m and v = 0. What is the displacement at t = π/5 s?",
    "options": [
      "a. −0.1 m",
      "b. 0.1 m",
      "c. 0 m",
      "d. 0.05 m"
    ],
    "answer": "a"
  },
  {
    "id": 302,
    "q": "A body undergoes SHM with amplitude A and angular frequency ω. At what displacement is the KE equal to the PE?",
    "options": [
      "a. A/√2",
      "b. A/2",
      "c. A√2/2",
      "d. A√3/2"
    ],
    "answer": "a"
  },
  {
    "id": 303,
    "q": "A rigid body has angular velocity vector ω = 3i − 2j + k rad/s. A point on the body is at r = i + 2j − k m. What is the velocity of that point?",
    "options": [
      "a. (0i + 4j + 8k) m/s",
      "b. (2i + 3j − k) m/s",
      "c. (−4j + 8k) m/s",
      "d. (0i + 4j − 8k) m/s"
    ],
    "answer": "a"
  },
  {
    "id": 304,
    "q": "What is the binding energy (total mechanical energy) of a satellite of mass m orbiting at radius r from Earth's centre (mass M)?",
    "options": [
      "a. −GMm/2r",
      "b. −GMm/r",
      "c. GMm/2r",
      "d. GMm/r"
    ],
    "answer": "a"
  },
  {
    "id": 305,
    "q": "A body of mass 5 kg is moving in a circle of radius 3 m with a speed that varies as v = 2t m/s. What is the net force on the body at t = 3 s?",
    "options": [
      "a. √(60² + 90²) ≈ 108.2 N",
      "b. 60 N",
      "c. 90 N",
      "d. √(10² + 60²) ≈ 60.8 N"
    ],
    "answer": "d"
  },
  {
    "id": 306,
    "q": "A particle of mass 2 kg has position r(t) = (t³ − 3t)i + (2t²)j m. What is the magnitude of the angular momentum about the origin at t = 2 s?",
    "options": [
      "a. 8 kg·m²/s",
      "b. 16 kg·m²/s",
      "c. 32 kg·m²/s",
      "d. 4 kg·m²/s"
    ],
    "answer": "c"
  },
  {
    "id": 307,
    "q": "A uniform sphere is released from rest on an inclined plane of angle θ. If it rolls without slipping, the linear acceleration is:",
    "options": [
      "a. 5g sinθ/7",
      "b. g sinθ",
      "c. 2g sinθ/3",
      "d. g sinθ/2"
    ],
    "answer": "a"
  },
  {
    "id": 308,
    "q": "If the angular momentum of a system is conserved and the moment of inertia decreases to half, the rotational kinetic energy:",
    "options": [
      "a. Doubles",
      "b. Halves",
      "c. Remains constant",
      "d. Quadruples"
    ],
    "answer": "a"
  },
  {
    "id": 309,
    "q": "A planet has twice the mass and twice the radius of Earth. What is the acceleration due to gravity on its surface compared to Earth's g?",
    "options": [
      "a. g/2",
      "b. 2g",
      "c. g/4",
      "d. g"
    ],
    "answer": "a"
  },
  {
    "id": 310,
    "q": "The escape velocity from Earth is 11.2 km/s. What is the escape velocity from a planet of same density but twice the radius?",
    "options": [
      "a. 22.4 km/s",
      "b. 5.6 km/s",
      "c. 11.2 km/s",
      "d. 15.8 km/s"
    ],
    "answer": "a"
  },
  {
    "id": 311,
    "q": "A satellite in a circular orbit of radius r has total energy E₁. It is moved to orbit of radius 2r. What is the new total energy E₂?",
    "options": [
      "a. E₂ = E₁/2",
      "b. E₂ = 2E₁",
      "c. E₂ = E₁",
      "d. E₂ = 4E₁"
    ],
    "answer": "a"
  },
  {
    "id": 312,
    "q": "A body of mass 5 kg is acted upon by the force F = (3t² − 2t)i N. If it starts from rest, what is its displacement in the first 2 s?",
    "options": [
      "a. 1.2 m",
      "b. 0.8 m",
      "c. 2.0 m",
      "d. 0.4 m"
    ],
    "answer": "b"
  },
  {
    "id": 313,
    "q": "The coefficient of restitution between two bodies is 0.6. Ball A (2 kg) at 4 m/s strikes stationary ball B (2 kg). What is the velocity of B after impact?",
    "options": [
      "a. 3.2 m/s",
      "b. 2.4 m/s",
      "c. 4.0 m/s",
      "d. 1.6 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 314,
    "q": "A particle moves along the curve y = x² in the x-y plane with constant speed of 2 m/s. At point (1, 1), what is the centripetal acceleration? (radius of curvature at that point is (1 + 4x²)^(3/2) / |2|; at x=1, R ≈ 5√5/2)",
    "options": [
      "a. ≈ 0.716 m/s²",
      "b. 1.0 m/s²",
      "c. 2.0 m/s²",
      "d. 4.0 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 315,
    "q": "A 3 kg ball hangs from the ceiling by two strings: one vertical and one at 45° to the vertical. What is the tension in the angled string? (g = 10 m/s²)",
    "options": [
      "a. 30√2 ≈ 42.4 N",
      "b. 30 N",
      "c. 15√2 ≈ 21.2 N",
      "d. 60 N"
    ],
    "answer": "a"
  },
  {
    "id": 316,
    "q": "A solid cylinder and a hollow cylinder of identical mass and radius roll without slipping with the same linear speed. What is the ratio of their kinetic energies KE_solid / KE_hollow?",
    "options": [
      "a. 3/4",
      "b. 4/3",
      "c. 1/2",
      "d. 2/3"
    ],
    "answer": "b"
  },
  {
    "id": 317,
    "q": "A 4 kg ball moving at 6 m/s strikes a wall and returns at 4 m/s at the same angle. Contact time is 0.05 s. What average force does the wall exert on the ball?",
    "options": [
      "a. 800 N",
      "b. 640 N",
      "c. 400 N",
      "d. 200 N"
    ],
    "answer": "a"
  },
  {
    "id": 318,
    "q": "A 2 kg mass is suspended from the centre of a 4 m long massless rod resting on two supports at the ends. The right support is replaced by a spring (k = 200 N/m). How much does the spring compress? (g = 10 m/s²)",
    "options": [
      "a. 0.05 m",
      "b. 0.1 m",
      "c. 0.025 m",
      "d. 0.2 m"
    ],
    "answer": "a"
  },
  {
    "id": 319,
    "q": "A 50 g bullet at 300 m/s passes through a 2 kg block and exits at 100 m/s. The block is on a rough surface (μk = 0.3). How far does the block slide? (g = 10 m/s²)",
    "options": [
      "a. 1.67 m",
      "b. 3.33 m",
      "c. 0.83 m",
      "d. 5.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 320,
    "q": "A body moving with SHM has a maximum displacement of 0.4 m and a maximum speed of 1.6 m/s. What is the period?",
    "options": [
      "a. π/2 s ≈ 1.57 s",
      "b. π s ≈ 3.14 s",
      "c. 2π/5 s",
      "d. 0.5 s"
    ],
    "answer": "a"
  },
  {
    "id": 321,
    "q": "What is the velocity of the 6 kg ball after an elastic head-on collision if it was initially at rest and was hit by a 2 kg ball moving at 9 m/s?",
    "options": [
      "a. 4.5 m/s",
      "b. 3 m/s",
      "c. 6 m/s",
      "d. 9 m/s"
    ],
    "answer": "b"
  },
  {
    "id": 322,
    "q": "A particle moves in a plane such that its position is r = e^t i + e^(−t) j m. What is the speed when t = 0?",
    "options": [
      "a. √2 m/s",
      "b. 2 m/s",
      "c. 0 m/s",
      "d. 1 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 323,
    "q": "A 5 kg, 2 m uniform rod is held horizontal by a hinge at one end and a vertical wire at the other. If the wire is cut, what is the angular acceleration of the rod immediately after? (g = 10 m/s², I_hinge = ML²/3)",
    "options": [
      "a. 7.5 rad/s²",
      "b. 5.0 rad/s²",
      "c. 15 rad/s²",
      "d. 3.75 rad/s²"
    ],
    "answer": "a"
  },
  {
    "id": 324,
    "q": "A particle moves with constant speed v in a circle. Which of the following correctly describes its acceleration?",
    "options": [
      "a. Constant magnitude, changing direction; always pointing toward centre",
      "b. Constant in both magnitude and direction",
      "c. Zero, since speed is constant",
      "d. Tangential only"
    ],
    "answer": "a"
  },
  {
    "id": 325,
    "q": "A body of mass 4 kg moving at 3 m/s east collides with a 6 kg body at rest. After collision, the 4 kg body moves at 1 m/s east. Is momentum conserved, and what is the velocity of the 6 kg body?",
    "options": [
      "a. Yes; 4/3 m/s east",
      "b. Yes; 2 m/s east",
      "c. No; momentum not conserved",
      "d. Yes; 0.5 m/s east"
    ],
    "answer": "a"
  },
  {
    "id": 326,
    "q": "The gravitational potential at the surface of a planet of mass M and radius R is V = −GM/R. What is the work done in moving a mass m from the surface to infinity?",
    "options": [
      "a. GMm/R",
      "b. −GMm/R",
      "c. 2GMm/R",
      "d. GMm/2R"
    ],
    "answer": "a"
  },
  {
    "id": 327,
    "q": "A block of mass 3 kg is tied by a horizontal string to the wall and rests on a wedge of angle 30° which is being pushed with force F. What is the tension in the string? (g = 10 m/s², tan30° = 0.577)",
    "options": [
      "a. 17.3 N",
      "b. 30 N",
      "c. 8.66 N",
      "d. 26 N"
    ],
    "answer": "a"
  },
  {
    "id": 328,
    "q": "A rod of length L with linear mass density λ = kx (where x is measured from one end) has total mass M = kL²/2. What is the distance of its centre of mass from the lighter end?",
    "options": [
      "a. 2L/3",
      "b. L/2",
      "c. L/3",
      "d. 3L/4"
    ],
    "answer": "a"
  },
  {
    "id": 329,
    "q": "A 10 kg uniform disk (R = 0.5 m) is pushed across a frictionless floor by a horizontal force F = 20 N applied at the rim, tangentially. What is the linear acceleration of the centre of mass?",
    "options": [
      "a. 2 m/s²",
      "b. 4 m/s²",
      "c. 1 m/s²",
      "d. 8 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 330,
    "q": "A ball on a string of length 1 m is hit tangentially giving it speed v₀ = 6 m/s at the bottom of a vertical circle. What maximum angle θ does it reach? (g = 10 m/s²)",
    "options": [
      "a. ≈ 80.4°",
      "b. 90°",
      "c. 60°",
      "d. 45°"
    ],
    "answer": "a"
  },
  {
    "id": 331,
    "q": "A uniform ladder of length L and mass m leans against a smooth wall at angle θ to the floor. What is the minimum coefficient of friction at the floor to prevent slipping?",
    "options": [
      "a. cosθ/(2sinθ) = (1/2)cotθ",
      "b. tanθ/2",
      "c. cotθ",
      "d. sinθ/cosθ"
    ],
    "answer": "a"
  },
  {
    "id": 332,
    "q": "A body of mass 2 kg is in equilibrium under three forces: F₁ = 10 N east, F₂ = 6 N north, and F₃ (unknown). What is F₃?",
    "options": [
      "a. (−10i − 6j) N, magnitude ≈ 11.66 N",
      "b. (10i + 6j) N",
      "c. (−10i + 6j) N",
      "d. (10i − 6j) N"
    ],
    "answer": "a"
  },
  {
    "id": 333,
    "q": "A bullet of mass 20 g is fired horizontally at 250 m/s into a ballistic pendulum of mass 2 kg suspended by 1 m strings. What maximum angle does the pendulum swing? (g = 10 m/s²)",
    "options": [
      "a. ≈ 18.9°",
      "b. ≈ 9.5°",
      "c. ≈ 36°",
      "d. ≈ 5°"
    ],
    "answer": "a"
  },
  {
    "id": 334,
    "q": "A homogeneous cylinder of mass M and radius R rolls without slipping inside a hollow cylinder of radius 3R. The period of small oscillations is:",
    "options": [
      "a. 2π√(4R/g)",
      "b. 2π√(2R/g)",
      "c. 2π√(R/g)",
      "d. 2π√(3R/g)"
    ],
    "answer": "a"
  },
  {
    "id": 335,
    "q": "A 5 kg block on a horizontal surface is connected by a spring (k = 200 N/m) to a fixed wall. The surface has μk = 0.15. The block is pulled 0.3 m from equilibrium and released. How far does it travel before first momentarily stopping? (g = 10 m/s²)",
    "options": [
      "a. 0.3 m",
      "b. 0.21 m",
      "c. 0.26 m",
      "d. 0.15 m"
    ],
    "answer": "c"
  },
  {
    "id": 336,
    "q": "A particle undergoes two successive displacements: d₁ = 3i + 4j m and d₂ = −i + 3j − 2k m. What is the magnitude of the total displacement?",
    "options": [
      "a. √53 ≈ 7.28 m",
      "b. √29 m",
      "c. 10 m",
      "d. √45 m"
    ],
    "answer": "a"
  },
  {
    "id": 337,
    "q": "A 10 kg cylinder (R = 0.4 m, I = ½MR²) is connected to a 4 kg hanging mass via an inextensible rope over the cylinder's axle. What is the acceleration? (g = 10 m/s²)",
    "options": [
      "a. 2.86 m/s²",
      "b. 4.0 m/s²",
      "c. 1.43 m/s²",
      "d. 5.71 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 338,
    "q": "A 3 kg mass moving east at 6 m/s and a 2 kg mass moving north at 9 m/s collide and stick together. What is the magnitude and direction of their common velocity?",
    "options": [
      "a. 4.33 m/s at 36.9° north of east",
      "b. 4.33 m/s at 53.1° north of east",
      "c. 3.60 m/s at 45° north of east",
      "d. 5.40 m/s at 30° north of east"
    ],
    "answer": "b"
  },
  {
    "id": 339,
    "q": "The velocity of a particle is v(t) = (4t³ − 6t) m/s. It starts at x = 2 m. What is its position at t = 2 s?",
    "options": [
      "a. 10 m",
      "b. 6 m",
      "c. 8 m",
      "d. 14 m"
    ],
    "answer": "a"
  },
  {
    "id": 340,
    "q": "A 6 kg block on a rough incline (μk = 0.25, θ = 30°) is pulled up at constant speed by a cable parallel to the incline. What is the cable tension? (g = 10 m/s², sin30° = 0.5, cos30° = 0.866)",
    "options": [
      "a. 42.99 N",
      "b. 30 N",
      "c. 12.99 N",
      "d. 60 N"
    ],
    "answer": "a"
  },
  {
    "id": 341,
    "q": "Two objects of mass 2 kg and 4 kg have momenta of equal magnitude but opposite direction. They collide and stick together. What is the common velocity?",
    "options": [
      "a. 0 m/s",
      "b. The velocity of the 2 kg object",
      "c. The velocity of the 4 kg object",
      "d. Cannot be determined"
    ],
    "answer": "a"
  },
  {
    "id": 342,
    "q": "A projectile is fired from the top of a cliff 80 m high at 20 m/s horizontally. What is the velocity just before impact? (g = 10 m/s²)",
    "options": [
      "a. √(400 + 1600) = √2000 ≈ 44.7 m/s",
      "b. 20 m/s",
      "c. 40 m/s",
      "d. 60 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 343,
    "q": "A solid sphere of mass 2 kg rolls without slipping and has translational KE = 5 J. What is its total KE? (I = 2/5 MR²)",
    "options": [
      "a. 7 J",
      "b. 10 J",
      "c. 5 J",
      "d. 12 J"
    ],
    "answer": "a"
  },
  {
    "id": 344,
    "q": "For a body executing SHM with ω = 4π rad/s and amplitude A = 0.05 m, what is the maximum velocity?",
    "options": [
      "a. 0.2π ≈ 0.628 m/s",
      "b. 0.4π ≈ 1.257 m/s",
      "c. 0.1π m/s",
      "d. π m/s"
    ],
    "answer": "a"
  },
  {
    "id": 345,
    "q": "What is the maximum height a 2 kg projectile reaches if its initial KE is 200 J and it is launched at 30° to the horizontal? (g = 10 m/s²)",
    "options": [
      "a. 5 m",
      "b. 10 m",
      "c. 2.5 m",
      "d. 20 m"
    ],
    "answer": "a"
  },
  {
    "id": 346,
    "q": "A 4 kg rigid body has principal moments of inertia I₁ = 2, I₂ = 3, I₃ = 5 kg·m². It rotates about principal axis 2 at 10 rad/s. What is the rotational KE?",
    "options": [
      "a. 150 J",
      "b. 100 J",
      "c. 250 J",
      "d. 300 J"
    ],
    "answer": "a"
  },
  {
    "id": 347,
    "q": "The force of gravity on a body is F = mg downward. Using Newton's 3rd law, what is the reaction force?",
    "options": [
      "a. mg upward on Earth, exerted by the body on Earth",
      "b. Normal force of ground on body",
      "c. mg upward exerted by the body on itself",
      "d. Tension in a rope"
    ],
    "answer": "a"
  },
  {
    "id": 348,
    "q": "A 2 kg body is thrown vertically upward with velocity 20 m/s. What is the work done by gravity during the entire upward journey? (g = 10 m/s²)",
    "options": [
      "a. −400 J",
      "b. 400 J",
      "c. −200 J",
      "d. 0 J"
    ],
    "answer": "a"
  },
  {
    "id": 349,
    "q": "A body is in equilibrium under the action of three concurrent forces. If one force is 10 N northward and another is 10 N eastward, the third force must be:",
    "options": [
      "a. 10√2 N at 45° south of west",
      "b. 10√2 N northward",
      "c. 20 N southwestward",
      "d. 10 N southward"
    ],
    "answer": "a"
  },
  {
    "id": 350,
    "q": "A 5 kg mass oscillates in SHM with equation x = 0.3 sin(6t) m. What is the maximum restoring force?",
    "options": [
      "a. 54 N",
      "b. 27 N",
      "c. 108 N",
      "d. 9 N"
    ],
    "answer": "a"
  },
  {
    "id": 351,
    "q": "The velocity of an object executing SHM changes from maximum v_max to half that value v_max/2. By what factor does the displacement change from zero?",
    "options": [
      "a. A√3/2",
      "b. A/2",
      "c. A√2/2",
      "d. A/√3"
    ],
    "answer": "a"
  },
  {
    "id": 352,
    "q": "Two satellites of equal mass orbit Earth at radii R and 4R respectively. What is the ratio of their orbital speeds v₁/v₂?",
    "options": [
      "a. 2",
      "b. 4",
      "c. 1/2",
      "d. 1/4"
    ],
    "answer": "a"
  },
  {
    "id": 353,
    "q": "A 5 kg block on a rough surface (μk = 0.3) is connected by a string over a pulley to a hanging mass. The system accelerates at 2 m/s². What is the hanging mass? (g = 10 m/s²)",
    "options": [
      "a. 2.08 kg",
      "b. 1.50 kg",
      "c. 2.50 kg",
      "d. 3.0 kg"
    ],
    "answer": "a"
  },
  {
    "id": 354,
    "q": "A 3 kg particle is subject to a centripetal force F = 27 N in a circle of radius 3 m. What is the kinetic energy of the particle?",
    "options": [
      "a. 40.5 J",
      "b. 81 J",
      "c. 20.25 J",
      "d. 27 J"
    ],
    "answer": "a"
  },
  {
    "id": 355,
    "q": "A wheel with I = 2 kg·m² at rest is acted on by a torque τ = (4t + 2) N·m. What is the angular velocity after 3 s?",
    "options": [
      "a. 12 rad/s",
      "b. 9 rad/s",
      "c. 21 rad/s",
      "d. 6 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 356,
    "q": "In a head-on elastic collision between a heavy mass M (moving) and a light mass m at rest (M >> m), the light mass will:",
    "options": [
      "a. Rebound at approximately twice the speed of M",
      "b. Remain at rest",
      "c. Move at the same speed as M",
      "d. Move at half the speed of M"
    ],
    "answer": "a"
  },
  {
    "id": 357,
    "q": "A 1 kg ball is thrown from a 20 m cliff at 15 m/s horizontally. What is the magnitude of its momentum just before hitting the ground? (g = 10 m/s²)",
    "options": [
      "a. ≈ 25 kg·m/s",
      "b. 15 kg·m/s",
      "c. 20 kg·m/s",
      "d. 35 kg·m/s"
    ],
    "answer": "a"
  },
  {
    "id": 358,
    "q": "Two unequal masses m₁ and m₂ (m₁ > m₂) are connected by a string on a frictionless surface. A force F is applied to m₁. What is the tension between them?",
    "options": [
      "a. Fm₂/(m₁ + m₂)",
      "b. Fm₁/(m₁ + m₂)",
      "c. F/(m₁ + m₂)",
      "d. F(m₁ − m₂)/(m₁ + m₂)"
    ],
    "answer": "a"
  },
  {
    "id": 359,
    "q": "A horizontal platform rotates at 2 rad/s. A 3 kg mass sits at 0.5 m from the centre. What additional torque is needed to maintain constant angular velocity when the mass is moved to 1 m?",
    "options": [
      "a. 0 N·m (no torque needed, angular momentum changes)",
      "b. 6 N·m",
      "c. 3 N·m",
      "d. 12 N·m"
    ],
    "answer": "a"
  },
  {
    "id": 360,
    "q": "A body of mass 2 kg executes SHM with amplitude 0.3 m and frequency 0.5 Hz. What is the maximum restoring force?",
    "options": [
      "a. 5.92 N",
      "b. 2.96 N",
      "c. 11.84 N",
      "d. 1.48 N"
    ],
    "answer": "a"
  },
  {
    "id": 361,
    "q": "At what height above the Earth's surface is the gravitational potential energy of a body equal to half of its value at the surface (taking U = 0 at infinity)? (R_E = 6400 km)",
    "options": [
      "a. 6400 km above surface",
      "b. 3200 km",
      "c. 12800 km",
      "d. 9600 km"
    ],
    "answer": "a"
  },
  {
    "id": 362,
    "q": "A disk starts from rest with angular acceleration α = 3t rad/s². How many revolutions does it complete in 4 s?",
    "options": [
      "a. 384/2π ≈ 6.1 rev",
      "b. 64/(2π) ≈ 10.2 rev",
      "c. 128/π ≈ 40.7 rev",
      "d. 192/π rev"
    ],
    "answer": "b"
  },
  {
    "id": 363,
    "q": "A 500 g ball is attached to a string of length 0.6 m and swings in a vertical circle. If the speed at the bottom is 3 m/s, what is the tension at the bottom? (g = 10 m/s²)",
    "options": [
      "a. 12.5 N",
      "b. 5 N",
      "c. 7.5 N",
      "d. 17.5 N"
    ],
    "answer": "a"
  },
  {
    "id": 364,
    "q": "A block of mass 4 kg is pulled by two ropes. Rope 1 exerts 30 N at 30° north of east, rope 2 exerts 20 N due east. What is the acceleration of the block?",
    "options": [
      "a. ≈ 11.9 m/s² at ≈ 17.8° N of E",
      "b. 12.5 m/s² due east",
      "c. 7.5 m/s² at 45° N of E",
      "d. 5.0 m/s² at 30° N of E"
    ],
    "answer": "a"
  },
  {
    "id": 365,
    "q": "A 2 kg mass performs circular motion of radius 0.5 m at constant speed. If the centripetal force is 8 N, how many revolutions per second does it make?",
    "options": [
      "a. 1/π rev/s ≈ 0.318 rev/s",
      "b. 2/π rev/s",
      "c. 1 rev/s",
      "d. π rev/s"
    ],
    "answer": "b"
  },
  {
    "id": 366,
    "q": "Which expression gives the angle θ at which the velocity vector makes with the horizontal for a projectile with initial speed v₀ at angle α, at time t?",
    "options": [
      "a. θ = arctan[(v₀sinα − gt)/(v₀cosα)]",
      "b. θ = arctan[(v₀cosα)/(v₀sinα − gt)]",
      "c. θ = arctan[(gt)/(v₀cosα)]",
      "d. θ = arctan[(v₀sinα + gt)/(v₀cosα)]"
    ],
    "answer": "a"
  },
  {
    "id": 367,
    "q": "A uniform cube of mass 5 kg and side 0.4 m is placed on a rough surface and a horizontal force F is applied at the top face. What is the maximum F before tipping? (g = 10 m/s²)",
    "options": [
      "a. 25 N",
      "b. 50 N",
      "c. 12.5 N",
      "d. 100 N"
    ],
    "answer": "a"
  },
  {
    "id": 368,
    "q": "A 60 kg athlete runs at 8 m/s along a 20 m radius circular track. What is the magnitude of the centripetal force?",
    "options": [
      "a. 1920 N",
      "b. 960 N",
      "c. 480 N",
      "d. 240 N"
    ],
    "answer": "b"
  },
  {
    "id": 369,
    "q": "A 3 kg block (μs = 0.5, μk = 0.4) on a horizontal surface is pushed by a gradually increasing force. At what force does it start to move, and what is the kinetic friction force once moving? (g = 10 m/s²)",
    "options": [
      "a. 15 N to start; 12 N kinetic",
      "b. 12 N to start; 15 N kinetic",
      "c. 15 N both",
      "d. 12 N both"
    ],
    "answer": "a"
  },
  {
    "id": 370,
    "q": "In an explosion, a stationary 10 kg object breaks into two pieces. Piece A (4 kg) moves at 15 m/s east. Piece B moves west at what speed?",
    "options": [
      "a. 10 m/s",
      "b. 6 m/s",
      "c. 15 m/s",
      "d. 37.5 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 371,
    "q": "A 2 kg mass on a spring (k = 800 N/m) oscillates. At t = 0 it is at x = 0.05 m and v = −1 m/s. What is the amplitude of oscillation?",
    "options": [
      "a. 0.0707 m",
      "b. 0.05 m",
      "c. 0.1 m",
      "d. 0.0354 m"
    ],
    "answer": "a"
  },
  {
    "id": 372,
    "q": "A uniform beam of mass 12 kg and length 4 m is hinged at a wall and supported by a horizontal cable attached at the free end, at 30° above the beam. A 20 kg mass hangs from the free end. What is the tension in the cable? (g = 10 m/s²)",
    "options": [
      "a. 640 N",
      "b. 320 N",
      "c. 240 N",
      "d. 160 N"
    ],
    "answer": "a"
  },
  {
    "id": 373,
    "q": "A 500 g projectile is launched at 40 m/s at 53° above horizontal. At the highest point, a small explosion breaks it into two equal pieces. One piece falls straight down. What is the speed of the other piece? (sin53° = 0.8, cos53° = 0.6)",
    "options": [
      "a. 48 m/s",
      "b. 24 m/s",
      "c. 40 m/s",
      "d. 12 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 374,
    "q": "A car of mass 1000 kg moves at 20 m/s. The driver applies brakes, decelerating at 5 m/s². What is the stopping distance?",
    "options": [
      "a. 40 m",
      "b. 80 m",
      "c. 20 m",
      "d. 100 m"
    ],
    "answer": "a"
  },
  {
    "id": 375,
    "q": "A 3 kg mass is suspended between two inclined planes making angles of 30° and 60° to the vertical. What are the normal forces N₁ and N₂ from the planes? (g = 10 m/s²)",
    "options": [
      "a. N₁ = 15 N, N₂ = 25.98 N",
      "b. N₁ = 25.98 N, N₂ = 15 N",
      "c. N₁ = N₂ = 15 N",
      "d. N₁ = 21.2 N, N₂ = 21.2 N"
    ],
    "answer": "a"
  },
  {
    "id": 376,
    "q": "A 4 kg particle at r = (2i + 3j) m has momentum p = (8i − 4j) kg·m/s. What is its angular momentum about the origin?",
    "options": [
      "a. (−32k) kg·m²/s",
      "b. (32k) kg·m²/s",
      "c. (−8k) kg·m²/s",
      "d. (56k) kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 377,
    "q": "Using the parallel-axis theorem, the moment of inertia of a solid sphere (I_cm = 2/5 MR²) about a tangential axis is:",
    "options": [
      "a. 7/5 MR²",
      "b. 2/5 MR² + MR²",
      "c. Both a and b are correct (they are equal)",
      "d. 12/5 MR²"
    ],
    "answer": "c"
  },
  {
    "id": 378,
    "q": "A block of mass 2 kg attached to a spring (k = 50 N/m) slides on a frictionless surface. At x = 0.2 m from equilibrium, v = 1.5 m/s. What is the total mechanical energy?",
    "options": [
      "a. 2.125 J",
      "b. 1.0 J",
      "c. 3.25 J",
      "d. 0.5 J"
    ],
    "answer": "a"
  },
  {
    "id": 379,
    "q": "The time of flight of a projectile is T. At what time during flight is the speed minimum?",
    "options": [
      "a. T/2 (at maximum height)",
      "b. At launch",
      "c. At impact",
      "d. T/4"
    ],
    "answer": "a"
  },
  {
    "id": 380,
    "q": "A rope connects a 6 kg block on a 37° incline (μk = 0.25) to a 4 kg block hanging vertically over a frictionless pulley. What is the acceleration? (g = 10 m/s², sin37° = 0.6, cos37° = 0.8)",
    "options": [
      "a. 1.0 m/s²",
      "b. 2.0 m/s²",
      "c. 3.0 m/s²",
      "d. 0.5 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 381,
    "q": "A 10 kg object falls from height h and penetrates 0.05 m into the ground before stopping. If the average resistance of the ground is 5000 N, what is h? (g = 10 m/s²)",
    "options": [
      "a. 2.5 m",
      "b. 5.0 m",
      "c. 0.25 m",
      "d. 1.25 m"
    ],
    "answer": "a"
  },
  {
    "id": 382,
    "q": "A uniform rod of mass M and length L hangs from a pivot at one end and is struck by a ball of mass m at the free end. The ball sticks to the rod. What is the angular velocity just after impact if the ball had speed v? (I_rod_pivot = ML²/3)",
    "options": [
      "a. 3mv/[(M + 3m)L]",
      "b. mv/(ML)",
      "c. 3mv/[ML]",
      "d. mv/[(M + m)L]"
    ],
    "answer": "a"
  },
  {
    "id": 383,
    "q": "A 2 kg block rests on a 5 kg block connected to a spring (k = 200 N/m) on a frictionless surface. The coefficient of friction between the two blocks is 0.3. What is the maximum amplitude of oscillation without the 2 kg block slipping? (g = 10 m/s²)",
    "options": [
      "a. 0.21 m",
      "b. 0.3 m",
      "c. 0.105 m",
      "d. 0.42 m"
    ],
    "answer": "a"
  },
  {
    "id": 384,
    "q": "A 1 kg particle moves in the xy-plane with angular momentum L = 6k kg·m²/s about the origin. If it moves in a circle of radius 2 m, what is its speed?",
    "options": [
      "a. 3 m/s",
      "b. 6 m/s",
      "c. 12 m/s",
      "d. 1.5 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 385,
    "q": "A particle has position r = A(cosωt i + sinωt j). Which of the following is true about its velocity and position?",
    "options": [
      "a. v ⊥ r at all times (v and r are always perpendicular)",
      "b. v ∥ r at all times",
      "c. v = r in magnitude",
      "d. v and r are at 45° to each other"
    ],
    "answer": "a"
  },
  {
    "id": 386,
    "q": "Two blocks of masses 3 kg and 5 kg are held against compressed spring on frictionless floor, then released. The 3 kg block moves at 10 m/s. What is the KE of the 5 kg block?",
    "options": [
      "a. 90 J",
      "b. 150 J",
      "c. 250 J",
      "d. 36 J"
    ],
    "answer": "a"
  },
  {
    "id": 387,
    "q": "A 4 kg pendulum bob is attached to a 2 m string. A horizontal force F pulls the bob until the string makes 45° with vertical. What is F? (g = 10 m/s²)",
    "options": [
      "a. 40 N",
      "b. 28.3 N",
      "c. 20 N",
      "d. 56.6 N"
    ],
    "answer": "a"
  },
  {
    "id": 388,
    "q": "A 5 kg mass moves in a circle of radius 2 m. At t = 0 the angular velocity is 3 rad/s and angular acceleration is 2 rad/s². What is the magnitude of total acceleration at t = 2 s?",
    "options": [
      "a. √(980 + 49) ≈ 32.1 m/s²",
      "b. 14 m/s²",
      "c. 10 m/s²",
      "d. √(196 + 400) ≈ 24.4 m/s²"
    ],
    "answer": "d"
  },
  {
    "id": 389,
    "q": "A spring of natural length 0.5 m and k = 300 N/m has a 2 kg mass attached. It hangs in equilibrium. By how much is it stretched? (g = 10 m/s²)",
    "options": [
      "a. 6.67 cm",
      "b. 3.33 cm",
      "c. 13.33 cm",
      "d. 1.0 cm"
    ],
    "answer": "a"
  },
  {
    "id": 390,
    "q": "A body of mass 3 kg has velocity v = 4i + 3j m/s and position r = 2i − j m at some instant. What is its angular momentum about the origin?",
    "options": [
      "a. (−14k) kg·m²/s",
      "b. (14k) kg·m²/s",
      "c. (−6k) kg·m²/s",
      "d. (6k) kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 391,
    "q": "By what factor does the escape velocity change if the planet's density is halved but its radius is doubled?",
    "options": [
      "a. 2",
      "b. √2",
      "c. 1",
      "d. 1/√2"
    ],
    "answer": "b"
  },
  {
    "id": 392,
    "q": "A block of mass 2 kg is released from the top of a 37° incline of length 3 m (μk = 0.3). It reaches the bottom and hits a spring (k = 500 N/m) on a horizontal surface. Maximum spring compression is: (g = 10 m/s², sin37° = 0.6, cos37° = 0.8)",
    "options": [
      "a. 0.224 m",
      "b. 0.15 m",
      "c. 0.3 m",
      "d. 0.45 m"
    ],
    "answer": "a"
  },
  {
    "id": 393,
    "q": "A rigid body rotating with angular momentum L has rotational kinetic energy KE = L²/2I. If L doubles and I triples, what happens to KE?",
    "options": [
      "a. KE becomes 4/3 of original",
      "b. KE doubles",
      "c. KE halves",
      "d. KE remains same"
    ],
    "answer": "a"
  },
  {
    "id": 394,
    "q": "A force F = F₀ sin(ωt) acts on a mass m at rest. What is the velocity at time t (where ω ≠ 0)?",
    "options": [
      "a. (F₀/mω)(1 − cosωt)",
      "b. (F₀/mω)cosωt",
      "c. F₀t/m",
      "d. (F₀/mω)sinωt"
    ],
    "answer": "a"
  },
  {
    "id": 395,
    "q": "A 2 kg block slides 3 m down a rough 45° incline then travels 2 m on a horizontal rough surface (μk = 0.3 on both surfaces) before stopping. What is the height of the incline? (g = 10 m/s²)",
    "options": [
      "a. ≈ 1.27 m",
      "b. 2.0 m",
      "c. 1.5 m",
      "d. 0.85 m"
    ],
    "answer": "a"
  },
  {
    "id": 396,
    "q": "Two masses M and m are connected by a massless rod of length d. They rotate freely about the rod's centre of mass. What is the kinetic energy if their common angular velocity is ω?",
    "options": [
      "a. MmωΩd²/2(M+m)",
      "b. (M+m)ω²d²/2",
      "c. Mmd²ω²/[2(M+m)]",
      "d. (M+m)ωd²/2"
    ],
    "answer": "c"
  },
  {
    "id": 398,
    "q": "If the kinetic energy of a body is doubled by increasing its speed, by what factor was the original speed increased?",
    "options": [
      "a. √2 − 1 (approximately 41.4%)",
      "b. 2 (100%)",
      "c. √2 (approximately 41.4% increase, factor √2)",
      "d. (√2 − 1) times"
    ],
    "answer": "c"
  },
  {
    "id": 399,
    "q": "The Moon orbits Earth in a nearly circular orbit at distance 3.84 × 10⁸ m with period 27.3 days. What is the centripetal acceleration of the Moon?",
    "options": [
      "a. 2.72 × 10⁻³ m/s²",
      "b. 9.8 m/s²",
      "c. 1.62 m/s²",
      "d. 6.67 × 10⁻³ m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 400,
    "q": "A 3 kg mass hangs from the end of a 4 m uniform rod (mass 2 kg) hinged at the wall. A vertical wire supports the rod at 1 m from the hinge. What is the tension in the wire? (g = 10 m/s²)",
    "options": [
      "a. 160 N",
      "b. 80 N",
      "c. 40 N",
      "d. 30 N"
    ],
    "answer": "a"
  },
  {
    "id": 401,
    "q": "What is the gravitational self-energy (gravitational potential energy) of a uniform solid sphere of mass M and radius R?",
    "options": [
      "a. −3GM²/5R",
      "b. −GM²/R",
      "c. −GM²/2R",
      "d. −3GM²/2R"
    ],
    "answer": "a"
  },
  {
    "id": 402,
    "q": "A particle is projected from a point on the ground at speed v₀ = 20 m/s. What angle maximises the horizontal range for landing on a slope inclined at 30° below horizontal? (g = 10 m/s²)",
    "options": [
      "a. 30° above horizontal",
      "b. 45° above horizontal",
      "c. 60° above horizontal",
      "d. 15° above horizontal"
    ],
    "answer": "d"
  },
  {
    "id": 403,
    "q": "Two forces P and Q have a resultant R. If P is doubled and Q is halved, and the angle between them is unchanged, what happens to R?",
    "options": [
      "a. Cannot determine without knowing original magnitudes and angle",
      "b. R doubles",
      "c. R is unchanged",
      "d. R halves"
    ],
    "answer": "a"
  },
  {
    "id": 404,
    "q": "A gyroscope of moment of inertia 0.01 kg·m² spins at 6000 rpm. A torque of 0.05 N·m is applied. What is the rate of precession?",
    "options": [
      "a. ≈ 0.00796 rad/s",
      "b. ≈ 0.05 rad/s",
      "c. ≈ 7.96 rad/s",
      "d. ≈ 50 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 405,
    "q": "A 5 kg sled on a frictionless icy surface is given a push of 20 N for 3 s. What is the final speed?",
    "options": [
      "a. 12 m/s",
      "b. 4 m/s",
      "c. 60 m/s",
      "d. 6 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 406,
    "q": "A body oscillating in SHM has the equation of motion a = −100x. What is the time period? (x in metres, a in m/s²)",
    "options": [
      "a. π/5 s ≈ 0.628 s",
      "b. 2π/10 s",
      "c. Both a and b are the same",
      "d. 2π/100 s"
    ],
    "answer": "c"
  },
  {
    "id": 407,
    "q": "A 2 kg block is connected to a spring (k = 200 N/m) and a dashpot (damping constant b = 8 N·s/m). The system is underdamped if:",
    "options": [
      "a. b² < 4mk; here 64 < 1600, so yes underdamped",
      "b. b² > 4mk",
      "c. b² = 4mk",
      "d. It is always underdamped"
    ],
    "answer": "a"
  },
  {
    "id": 408,
    "q": "What is the minimum speed needed at the top of a loop-the-loop of radius 5 m to maintain contact? (g = 10 m/s²)",
    "options": [
      "a. √50 ≈ 7.07 m/s",
      "b. 10 m/s",
      "c. 5 m/s",
      "d. √100 = 10 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 409,
    "q": "A 6 kg mass is placed 2 m from the pivot of a see-saw, and a 4 kg mass is on the other side. For equilibrium, where must the 4 kg mass sit?",
    "options": [
      "a. 3 m from pivot",
      "b. 2 m from pivot",
      "c. 1.5 m from pivot",
      "d. 4 m from pivot"
    ],
    "answer": "a"
  },
  {
    "id": 410,
    "q": "A 5 kg mass on a frictionless table is connected via string over a frictionless edge to a hanging 3 kg mass. A second string pulls the 5 kg mass backward with force T = 4 N. What is the system acceleration? (g = 10 m/s²)",
    "options": [
      "a. 3.25 m/s²",
      "b. 2.0 m/s²",
      "c. 5.0 m/s²",
      "d. 4.5 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 411,
    "q": "A 2 kg mass undergoes SHM with period 4 s. At t = 0, x = 0.5 m and v = 0. What is the velocity at x = 0.3 m?",
    "options": [
      "a. ±0.628 m/s",
      "b. ±0.4 m/s",
      "c. ±0.314 m/s",
      "d. ±1.0 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 412,
    "q": "A horizontal force F is applied to a wheel of radius R and moment of inertia I = MR²/2. The wheel rolls without slipping on a flat surface. What is the linear acceleration of the wheel's centre?",
    "options": [
      "a. 2F/(3M)",
      "b. F/M",
      "c. F/(2M)",
      "d. 2F/M"
    ],
    "answer": "a"
  },
  {
    "id": 413,
    "q": "A particle moves with position x = 3sin²(t) m. What is the angular frequency of oscillation embedded in this motion?",
    "options": [
      "a. 2 rad/s (from x = 3/2 − 3/2 cos(2t))",
      "b. 1 rad/s",
      "c. 4 rad/s",
      "d. 0.5 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 414,
    "q": "A body of mass 3 kg has kinetic energy increasing at a rate of 30 W at an instant when its speed is 5 m/s. What is the net force on the body at that instant?",
    "options": [
      "a. 6 N",
      "b. 10 N",
      "c. 2 N",
      "d. 15 N"
    ],
    "answer": "a"
  },
  {
    "id": 415,
    "q": "In which of these situations is angular momentum about the centre conserved for a single particle moving on a curved path?",
    "options": [
      "a. When the net torque about the centre is zero (central force)",
      "b. Always",
      "c. Only in circular motion",
      "d. Only in SHM"
    ],
    "answer": "a"
  },
  {
    "id": 416,
    "q": "A 2 kg ball is thrown at an angle of 45° at 20 m/s. What is the magnitude of the angular momentum of the ball about the launch point at the highest point of its trajectory? (g = 10 m/s²)",
    "options": [
      "a. 283.1 kg·m²/s",
      "b. 141.4 kg·m²/s",
      "c. 400 kg·m²/s",
      "d. 200 kg·m²/s"
    ],
    "answer": "a"
  },
  {
    "id": 417,
    "q": "A vehicle accelerates uniformly from 0 to 20 m/s in 10 s. What is the average power delivered if the vehicle's mass is 1000 kg and there is a constant friction of 500 N?",
    "options": [
      "a. 25,000 W",
      "b. 20,000 W",
      "c. 15,000 W",
      "d. 10,000 W"
    ],
    "answer": "a"
  },
  {
    "id": 418,
    "q": "A 1 kg object on a spring (k = 100 N/m) has initial displacement x₀ = 0.3 m and v₀ = 0. Another 1 kg object collides and sticks to it (inelastic) while the spring is at natural length with v = 2 m/s. What is the new amplitude?",
    "options": [
      "a. √(0.01 + 0.09) = √0.1 ≈ 0.316 m",
      "b. 0.3 m",
      "c. 0.1 m",
      "d. 0.2 m"
    ],
    "answer": "c"
  },
  {
    "id": 419,
    "q": "A 4 kg, 1 m rod is hinged at one end and lies horizontally. A point mass of 2 kg is attached at 0.6 m from the hinge. The rod is given angular velocity ω₀ = 3 rad/s. How high does the centre of mass rise? (g = 10 m/s², I_rod = ML²/3)",
    "options": [
      "a. 0.162 m",
      "b. 0.324 m",
      "c. 0.081 m",
      "d. 0.45 m"
    ],
    "answer": "a"
  },
  {
    "id": 420,
    "q": "A 5 kg block on a rough horizontal surface (μk = 0.2) is connected to a spring (k = 200 N/m). It is displaced 0.15 m and released. What is the maximum speed during the subsequent motion? (g = 10 m/s²)",
    "options": [
      "a. 0.894 m/s",
      "b. 1.5 m/s",
      "c. 0.447 m/s",
      "d. 1.0 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 421,
    "q": "A uniform rod of mass 4 kg and length 3 m rotates freely about a vertical axis through its centre. A torque of 6 N·m is applied for 5 s. What is the angular velocity? (I = ML²/12)",
    "options": [
      "a. 20 rad/s",
      "b. 10 rad/s",
      "c. 5 rad/s",
      "d. 40 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 422,
    "q": "A 3 kg and a 2 kg block are separated by a spring (k = 500 N/m) and compressed by 0.1 m. They are released on a frictionless surface. What are their speeds after the spring reaches its natural length?",
    "options": [
      "a. v₃ = √(500/3)/10 ≈ 1.29 m/s, v₂ ≈ 1.94 m/s",
      "b. Both move at the same speed",
      "c. Only the lighter block moves",
      "d. v₃ = 1.0, v₂ = 1.5 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 423,
    "q": "A particle of mass m moves under a force F = −kx + bx³ (non-linear spring). Near equilibrium, for small displacements, it behaves as:",
    "options": [
      "a. Simple harmonic oscillator with ω = √(k/m)",
      "b. Non-oscillatory",
      "c. SHM with ω = √(b/m)",
      "d. SHM with increasing amplitude"
    ],
    "answer": "a"
  },
  {
    "id": 424,
    "q": "A 10 kg mass is suspended by two strings of lengths 3 m and 4 m attached to two points 5 m apart on the same horizontal level. What are the tensions T₁ and T₂? (g = 10 m/s²)",
    "options": [
      "a. T₁ = 80 N, T₂ = 60 N",
      "b. T₁ = 60 N, T₂ = 80 N",
      "c. T₁ = T₂ = 70 N",
      "d. T₁ = 50 N, T₂ = 100 N"
    ],
    "answer": "a"
  },
  {
    "id": 425,
    "q": "A comet moves in an elliptical orbit around the sun. At perihelion (r_p = 10¹¹ m) its speed is 60 km/s. What is its speed at aphelion (r_a = 6 × 10¹¹ m)?",
    "options": [
      "a. 10 km/s",
      "b. 360 km/s",
      "c. 6 km/s",
      "d. 30 km/s"
    ],
    "answer": "a"
  },
  {
    "id": 426,
    "q": "A uniform disc (mass M, radius R) and a ring (mass M, radius R) start from rest at the top of an incline. Which reaches the bottom first and why?",
    "options": [
      "a. Disc; it has smaller I/MR² ratio (1/2) vs ring (1), so less rotational inertia relative to mass",
      "b. Ring; lighter moment of inertia",
      "c. Both reach simultaneously",
      "d. Depends on the incline angle"
    ],
    "answer": "a"
  },
  {
    "id": 427,
    "q": "A 1200 kg car travelling at 25 m/s skids to a stop. If μk = 0.5, what is the stopping distance? (g = 10 m/s²)",
    "options": [
      "a. 62.5 m",
      "b. 31.25 m",
      "c. 125 m",
      "d. 50 m"
    ],
    "answer": "a"
  },
  {
    "id": 428,
    "q": "A particle's motion in the x-direction is x = 5 + 3cos(2t) m. What is the equilibrium position, amplitude, and angular frequency?",
    "options": [
      "a. x₀ = 5 m, A = 3 m, ω = 2 rad/s",
      "b. x₀ = 0 m, A = 5 m, ω = 3 rad/s",
      "c. x₀ = 3 m, A = 5 m, ω = 2 rad/s",
      "d. x₀ = 5 m, A = 2 m, ω = 3 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 429,
    "q": "Using energy methods, a 3 kg block compresses a spring (k = 900 N/m) by 0.2 m. The spring fires the block up a frictionless 37° incline. How far along the incline does the block travel? (sin37° = 0.6, g = 10 m/s²)",
    "options": [
      "a. 1.0 m",
      "b. 2.0 m",
      "c. 0.5 m",
      "d. 1.5 m"
    ],
    "answer": "a"
  },
  {
    "id": 430,
    "q": "A 2 kg block on a horizontal frictionless surface is attached to a wall spring (k = 800 N/m) and oscillates. A 0.5 kg lump of clay is dropped vertically onto the block when the block passes through equilibrium at v = 4 m/s. What is the new amplitude?",
    "options": [
      "a. 0.16 m",
      "b. 0.32 m",
      "c. 0.08 m",
      "d. 0.2 m"
    ],
    "answer": "a"
  },
  {
    "id": 431,
    "q": "A projectile is fired at angle θ from a cliff of height H. The range on the ground below is R. Show that for maximum range, the optimal angle satisfies: tan(2θ) = −R/H. For H = 20 m, g = 10 m/s², v₀ = 20 m/s, what angle maximises range?",
    "options": [
      "a. ≈ 34.3°",
      "b. 45°",
      "c. 30°",
      "d. 60°"
    ],
    "answer": "a"
  },
  {
    "id": 432,
    "q": "A 3 kg body moves under the conservative force F = (6x − 4)i N. Find the potential energy as a function of x if U = 0 at x = 1 m.",
    "options": [
      "a. U = −3x² + 4x − 1 J",
      "b. U = 3x² − 4x + 1 J",
      "c. U = 6x − 4 J",
      "d. U = 3x² + 4x J"
    ],
    "answer": "a"
  },
  {
    "id": 433,
    "q": "A 5 kg mass on a frictionless surface oscillates on a spring with A = 0.2 m and T = 2 s. What is the spring constant k?",
    "options": [
      "a. ≈ 49.3 N/m",
      "b. 5 N/m",
      "c. 20 N/m",
      "d. 100 N/m"
    ],
    "answer": "a"
  },
  {
    "id": 434,
    "q": "Two masses m₁ = 1 kg and m₂ = 3 kg move toward each other at 4 m/s and 2 m/s respectively. They undergo a perfectly elastic collision. What are their final velocities?",
    "options": [
      "a. v₁ = −5 m/s, v₂ = 1 m/s",
      "b. v₁ = 5 m/s, v₂ = −1 m/s",
      "c. v₁ = 2 m/s, v₂ = −4 m/s",
      "d. v₁ = −3 m/s, v₂ = 3 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 435,
    "q": "A rigid body undergoes rotation. Euler's equation for torque about a principal axis is τ₁ = I₁(dω₁/dt) − (I₂ − I₃)ω₂ω₃. If τ = 0 (torque-free), I₁ = I₂ ≠ I₃, and ω₃ ≠ 0, the body undergoes:",
    "options": [
      "a. Steady precession (torque-free precession)",
      "b. Pure spinning",
      "c. Nutation only",
      "d. No rotation"
    ],
    "answer": "a"
  },
  {
    "id": 436,
    "q": "A particle of mass m moves in a potential U = ½kx² + ½bx⁴ where b > 0. For small oscillations, the effective spring constant is:",
    "options": [
      "a. k",
      "b. k + 3bA²/2 (amplitude-dependent softening)",
      "c. k − b",
      "d. k + b"
    ],
    "answer": "a"
  },
  {
    "id": 437,
    "q": "A 4 kg disc (I = ½MR², R = 0.5 m) rotates at 20 rad/s. It is placed flat on a rough surface (μk = 0.4). How long does it take to stop? (g = 10 m/s²)",
    "options": [
      "a. ≈ 1.27 s",
      "b. 2.55 s",
      "c. 0.63 s",
      "d. 5.0 s"
    ],
    "answer": "a"
  },
  {
    "id": 438,
    "q": "A particle is projected from ground level at 30° with a speed of 40 m/s. What is the radius of curvature of the trajectory at the highest point? (g = 10 m/s²)",
    "options": [
      "a. 120 m",
      "b. 240 m",
      "c. 80 m",
      "d. 60 m"
    ],
    "answer": "a"
  },
  {
    "id": 439,
    "q": "A block of mass m on a frictionless incline of angle θ connected via string over a pulley to mass M hanging vertically. The system is in equilibrium when M = m sinθ. If M is slightly increased to M + δM, the acceleration is approximately:",
    "options": [
      "a. δMg/(M + m)",
      "b. δMg/m",
      "c. g",
      "d. δMg/M"
    ],
    "answer": "a"
  },
  {
    "id": 441,
    "q": "Two particles of masses m and 2m move in circles of radii r and 2r respectively with the same angular velocity ω. What is the ratio of their centripetal forces F_m / F_{2m}?",
    "options": [
      "a. 1/4",
      "b. 1/2",
      "c. 1",
      "d. 2"
    ],
    "answer": "a"
  },
  {
    "id": 442,
    "q": "A uniform plank of mass 20 kg and length 8 m is pivoted at its left end. How far from the left end should a 30 kg mass be placed to balance the plank?",
    "options": [
      "a. 10/3 m ≈ 3.33 m",
      "b. 4 m",
      "c. 2 m",
      "d. 5 m"
    ],
    "answer": "a"
  },
  {
    "id": 443,
    "q": "A 2 kg ball is tied to a 1 m string and moves in a horizontal circle such that the string makes 60° with the vertical. If the string can handle a maximum tension of 40 N, what is the maximum speed? (g = 10 m/s²)",
    "options": [
      "a. 3.46 m/s",
      "b. 4.47 m/s",
      "c. 5.48 m/s",
      "d. 2.45 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 444,
    "q": "In a elastic collision between two objects where one is initially at rest, which of the following is always true?",
    "options": [
      "a. Both kinetic energy and momentum are conserved",
      "b. Only momentum is conserved",
      "c. Only kinetic energy is conserved",
      "d. Neither is conserved"
    ],
    "answer": "a"
  },
  {
    "id": 445,
    "q": "A 1500 W motor drives a conveyor belt. The belt moves at 5 m/s. What is the maximum mass it can move horizontally against a friction force equal to 0.1 × mg? (g = 10 m/s²)",
    "options": [
      "a. 300 kg",
      "b. 150 kg",
      "c. 30 kg",
      "d. 3000 kg"
    ],
    "answer": "a"
  },
  {
    "id": 446,
    "q": "A 10 kg mass falls from height h onto a platform of mass 5 kg connected to a spring (k = 2000 N/m). The collision is perfectly inelastic. What is h if maximum spring compression is 0.3 m? (g = 10 m/s²)",
    "options": [
      "a. ≈ 0.25 m",
      "b. ≈ 0.50 m",
      "c. ≈ 0.15 m",
      "d. ≈ 1.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 447,
    "q": "What is the maximum range of a projectile on a horizontal plane if the initial speed is 30 m/s? (g = 10 m/s²)",
    "options": [
      "a. 90 m",
      "b. 45 m",
      "c. 180 m",
      "d. 60 m"
    ],
    "answer": "a"
  },
  {
    "id": 448,
    "q": "A particle undergoes circular motion with radius 4 m. Its speed at angle θ = 0 is 3 m/s with tangential acceleration aₜ = 2 m/s². What is the total acceleration when θ = π/2 (after traveling a quarter circle)?",
    "options": [
      "a. √(169/4 + 4) ≈ 7.07 m/s²",
      "b. 5 m/s²",
      "c. 8 m/s²",
      "d. √(25 + 4) ≈ 5.39 m/s²"
    ],
    "answer": "d"
  },
  {
    "id": 449,
    "q": "An engine does work on a body described by the power equation P = 3t² W. The body starts from rest. If the mass is 6 kg, what is the velocity at t = 2 s?",
    "options": [
      "a. 2 m/s",
      "b. 4 m/s",
      "c. 8 m/s",
      "d. 3 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 450,
    "q": "A 2 kg mass is launched vertically at 30 m/s. A 1 kg mass is simultaneously projected at the same speed from 10 m higher. At what time and height do they meet? (g = 10 m/s²)",
    "options": [
      "a. t = 1/3 s, h ≈ 9.44 m",
      "b. t = 1 s, h = 25 m",
      "c. t = 0.5 s, h = 13.75 m",
      "d. They never meet"
    ],
    "answer": "a"
  },
  {
    "id": 451,
    "q": "A 5 kg block is on a rough surface (μk = 0.3). A spring (k = 500 N/m) is attached to a wall and to the block. The block is displaced 0.2 m and released. After the first half oscillation, how much energy has been lost to friction? (g = 10 m/s²)",
    "options": [
      "a. 6 J",
      "b. 3 J",
      "c. 1.5 J",
      "d. 12 J"
    ],
    "answer": "a"
  },
  {
    "id": 452,
    "q": "A body moving at 10 m/s is subject to a resistance force F_r = kv² where k = 0.5 N·s²/m². If the mass is 2 kg, what is the instantaneous deceleration?",
    "options": [
      "a. 25 m/s²",
      "b. 50 m/s²",
      "c. 2.5 m/s²",
      "d. 5 m/s²"
    ],
    "answer": "a"
  },
  {
    "id": 453,
    "q": "Two elastic spheres collide. Sphere 1 (2 kg) moving at 6 m/s east hits sphere 2 (4 kg) moving at 2 m/s west. Find v₁' and v₂' after elastic collision.",
    "options": [
      "a. v₁' = −6 m/s, v₂' = 2 m/s",
      "b. v₁' = −2 m/s, v₂' = 4 m/s",
      "c. v₁' = −10/3 m/s, v₂' = 8/3 m/s",
      "d. v₁' = 0, v₂' = 3 m/s"
    ],
    "answer": "c"
  },
  {
    "id": 454,
    "q": "A planet orbits a star in an elliptical orbit. At aphelion (r_a = 1.5 AU), its speed is 20 km/s. What is its speed at perihelion (r_p = 0.5 AU)?",
    "options": [
      "a. 60 km/s",
      "b. 40 km/s",
      "c. 30 km/s",
      "d. 10 km/s"
    ],
    "answer": "a"
  },
  {
    "id": 455,
    "q": "A 4 kg mass sits on top of a spring (k = 1600 N/m) at the base of a frictionless incline of 30°. The spring is compressed 0.25 m and released. How far up the incline does the mass slide? (g = 10 m/s², sin30° = 0.5)",
    "options": [
      "a. 1.0 m",
      "b. 2.0 m",
      "c. 0.5 m",
      "d. 4.0 m"
    ],
    "answer": "b"
  },
  {
    "id": 456,
    "q": "A 3 kg block at rest on a frictionless surface is struck by a 1 kg ball at 8 m/s. After impact, the ball moves at 2 m/s in the same direction. Is the collision elastic or inelastic?",
    "options": [
      "a. Inelastic (KE before = 32 J; KE after = 2 + 4.5 = 6.5 J; not equal)",
      "b. Elastic (KE conserved)",
      "c. Perfectly inelastic",
      "d. Cannot determine"
    ],
    "answer": "a"
  },
  {
    "id": 457,
    "q": "A rotating platform of mass 100 kg and radius 2 m (I = ½MR²) is rotating at 3 rad/s. A 50 kg person stands at the rim. The person walks to the centre. What is the new angular velocity?",
    "options": [
      "a. 5 rad/s",
      "b. 4 rad/s",
      "c. 6 rad/s",
      "d. 3 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 458,
    "q": "A mass m₁ = 2 kg moving at 10 m/s north and m₂ = 2 kg moving at 10 m/s east collide and stick together. What is the speed of the combined mass?",
    "options": [
      "a. 10/√2 ≈ 7.07 m/s",
      "b. 10 m/s",
      "c. 5 m/s",
      "d. 20 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 459,
    "q": "A 10 g bullet is fired at 500 m/s into a 490 g block. The block-bullet system rises to a height h. What is h? (g = 10 m/s²)",
    "options": [
      "a. 0.25 m",
      "b. 0.5 m",
      "c. 1.0 m",
      "d. 2.5 m"
    ],
    "answer": "a"
  },
  {
    "id": 460,
    "q": "The angular momentum of a planet about the Sun is constant (Kepler's second law). This is because:",
    "options": [
      "a. The gravitational force is always directed toward the Sun (central force, zero torque)",
      "b. Gravity is conservative",
      "c. The orbit is elliptical",
      "d. The planet's speed is constant"
    ],
    "answer": "a"
  },
  {
    "id": 461,
    "q": "A particle at position r = (2i + 3j − k) m has force F = (i − 2j + 4k) N acting on it. What is the torque about the origin?",
    "options": [
      "a. (10i − 9j − 7k) N·m",
      "b. (2i − 6j − 4k) N·m",
      "c. (10i + 9j − 7k) N·m",
      "d. (−10i + 9j + 7k) N·m"
    ],
    "answer": "a"
  },
  {
    "id": 462,
    "q": "A 2 kg mass is constrained to move on a smooth horizontal surface and is connected to a fixed point by a spring (k = 200 N/m) and by a string wrapped around a drum of mass 1 kg and radius 0.1 m. What is the effective k for the system?",
    "options": [
      "a. 200 N/m (drum contributes to inertia but not stiffness)",
      "b. 400 N/m",
      "c. 100 N/m",
      "d. 150 N/m"
    ],
    "answer": "a"
  },
  {
    "id": 463,
    "q": "A wheel starts at rest, accelerates at 5 rad/s² for 10 s, then decelerates uniformly and stops in 20 s. How many total revolutions does it make?",
    "options": [
      "a. 119.4 rev",
      "b. 59.7 rev",
      "c. 79.6 rev",
      "d. 239 rev"
    ],
    "answer": "a"
  },
  {
    "id": 464,
    "q": "A horizontal force F = 30 N is applied at height h = 0.8 m on a block of mass 5 kg and height 1 m on a rough surface (μs = 0.5). Does the block slide or tip first? (g = 10 m/s²)",
    "options": [
      "a. Tips first; tipping torque < sliding threshold",
      "b. Slides first",
      "c. Both occur simultaneously",
      "d. Neither occurs"
    ],
    "answer": "b"
  },
  {
    "id": 465,
    "q": "For an SHM oscillator, the phase space trajectory (x vs v) is:",
    "options": [
      "a. An ellipse",
      "b. A circle",
      "c. A straight line",
      "d. A parabola"
    ],
    "answer": "a"
  },
  {
    "id": 466,
    "q": "A 0.5 kg mass on a frictionless horizontal surface is attached to a vertical wall by a spring (k = 50 N/m). When x = 0.08 m, v = 0.6 m/s. What is the amplitude?",
    "options": [
      "a. 0.1 m",
      "b. 0.08 m",
      "c. 0.12 m",
      "d. 0.14 m"
    ],
    "answer": "a"
  },
  {
    "id": 467,
    "q": "Kepler's third law states T² ∝ r³ for planets orbiting the Sun. Earth has r = 1 AU, T = 1 yr. A planet at r = 4 AU has period:",
    "options": [
      "a. 8 years",
      "b. 4 years",
      "c. 16 years",
      "d. 2 years"
    ],
    "answer": "a"
  },
  {
    "id": 468,
    "q": "A 2000 kg truck moving at 15 m/s hits a stationary 500 kg car. They lock together. What percentage of the initial KE is lost?",
    "options": [
      "a. 20%",
      "b. 40%",
      "c. 60%",
      "d. 80%"
    ],
    "answer": "a"
  },
  {
    "id": 469,
    "q": "A string is attached to two walls 2 m apart. The string is 2.5 m long with a 4 kg mass hanging from its midpoint. What is the tension in each half of the string? (g = 10 m/s²)",
    "options": [
      "a. 26.7 N",
      "b. 20 N",
      "c. 40 N",
      "d. 13.3 N"
    ],
    "answer": "a"
  },
  {
    "id": 470,
    "q": "A body of mass m is moving in a circle under gravity on the inside of a vertical cone of half-angle α. For uniform circular motion at radius r from the axis, what is the speed?",
    "options": [
      "a. √(gr tanα)",
      "b. √(gr/tanα)",
      "c. √(g tanα/r)",
      "d. √(gr cosα)"
    ],
    "answer": "a"
  },
  {
    "id": 471,
    "q": "A spring-mass system has ω₀ = 10 rad/s. A driving force F = F₀ cos(8t) is applied. What is the amplitude ratio at resonance compared to this driving frequency? (ignore damping)",
    "options": [
      "a. The steady-state amplitude at ω = 8 is A(8); at resonance (ω = 10) amplitude diverges without damping",
      "b. 1/36",
      "c. 36/1",
      "d. Amplitudes are equal"
    ],
    "answer": "a"
  },
  {
    "id": 472,
    "q": "A 3 kg mass is in equilibrium hanging from two springs in series (k₁ = 100 N/m, k₂ = 200 N/m). What is the total extension? (g = 10 m/s²)",
    "options": [
      "a. 0.45 m",
      "b. 0.225 m",
      "c. 0.1 m",
      "d. 0.15 m"
    ],
    "answer": "a"
  },
  {
    "id": 473,
    "q": "If two springs of equal natural length L and spring constants k₁ and k₂ are connected in parallel, the effective spring constant is:",
    "options": [
      "a. k₁ + k₂",
      "b. k₁k₂/(k₁ + k₂)",
      "c. (k₁ + k₂)/2",
      "d. 1/(k₁ + k₂)"
    ],
    "answer": "a"
  },
  {
    "id": 474,
    "q": "A 4 kg mass on a frictionless horizontal surface is connected by a horizontal spring (k = 400 N/m) to a wall. At x = 0.1 m, v = −2 m/s. Which way is the spring stretched, and what is the amplitude?",
    "options": [
      "a. Spring stretched 0.1 m; A = √(0.01 + 0.04) = √0.05 ≈ 0.224 m",
      "b. A = 0.1 m",
      "c. A = 0.3 m",
      "d. A = 0.2 m"
    ],
    "answer": "a"
  },
  {
    "id": 475,
    "q": "A pendulum clock is accurate at sea level (g = 9.8 m/s²). It is taken to a mountain where g = 9.79 m/s². By approximately how much does it gain or lose per day?",
    "options": [
      "a. Loses ≈ 44 s/day",
      "b. Gains ≈ 44 s/day",
      "c. Loses ≈ 88 s/day",
      "d. Neither; period is unchanged"
    ],
    "answer": "a"
  },
  {
    "id": 476,
    "q": "A 6 kg block is pushed against a wall (μs = 0.4) by a horizontal force F. What is the minimum F to prevent the block from sliding down? (g = 10 m/s²)",
    "options": [
      "a. 150 N",
      "b. 60 N",
      "c. 240 N",
      "d. 24 N"
    ],
    "answer": "a"
  },
  {
    "id": 477,
    "q": "A uniform square plate of side a and mass M is free to rotate about one edge. It is held horizontal and released. What is the angular acceleration initially? (g = 10 m/s², I_edge = 4Ma²/3 for a square)",
    "options": [
      "a. 3g/(2a)",
      "b. g/a",
      "c. g/(2a)",
      "d. 2g/a"
    ],
    "answer": "a"
  },
  {
    "id": 478,
    "q": "A 10 kg ball is dropped from rest from 45 m. At what height above ground is its KE equal to twice its PE? (g = 10 m/s²; take PE = 0 at ground)",
    "options": [
      "a. 15 m",
      "b. 30 m",
      "c. 22.5 m",
      "d. 10 m"
    ],
    "answer": "a"
  },
  {
    "id": 479,
    "q": "A particle of mass 3 kg is in a potential energy field U = 3x² − 12x + 9 J. Find the equilibrium position and determine if it is stable.",
    "options": [
      "a. x = 2 m; stable (U has a minimum there)",
      "b. x = 2 m; unstable",
      "c. x = 3 m; stable",
      "d. x = 1 m; stable"
    ],
    "answer": "a"
  },
  {
    "id": 480,
    "q": "A ball is tied to two strings of equal length attached to the ceiling and floor directly above/below each other (same vertical line), 2 m apart. The strings are taut. If the ball is hit tangentially and moves in a horizontal circle, the lower string goes slack when:",
    "options": [
      "a. Centripetal acceleration > g·cotθ for upper string angle θ",
      "b. Speed exceeds √(gL)",
      "c. Never; both strings remain taut",
      "d. Lower string always slack in circular motion"
    ],
    "answer": "a"
  },
  {
    "id": 481,
    "q": "A block of mass 3 kg slides off a table of height 1.2 m with horizontal velocity 4 m/s. What is the distance from the base of the table to where it lands? (g = 10 m/s²)",
    "options": [
      "a. 1.97 m",
      "b. 2.4 m",
      "c. 1.0 m",
      "d. 3.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 482,
    "q": "A ring of mass M and radius R can spin freely about its vertical axis. A point mass m slides inward from the rim to the centre along a smooth horizontal rod fixed to the ring. Initial ω₀ with mass at rim; final ω when mass at centre:",
    "options": [
      "a. ω = ω₀(1 + m/M) for m at rim",
      "b. ω = ω₀(MR²)/(MR² + mR²)",
      "c. ω = ω₀ (conserved trivially)",
      "d. ω = ω₀(MR² + mR²)/(MR²)"
    ],
    "answer": "d"
  },
  {
    "id": 483,
    "q": "A 500 g, 1 m uniform rod is hinged at one end at the ceiling. A bullet of 10 g at 300 m/s embeds at the free end. What is the angular velocity just after impact?",
    "options": [
      "a. ≈ 17.1 rad/s",
      "b. 6 rad/s",
      "c. 30 rad/s",
      "d. 3 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 484,
    "q": "A disc of mass M and radius R rolls without slipping on a horizontal surface. A force F is applied horizontally at the centre. What is the friction force at the contact point?",
    "options": [
      "a. F/3",
      "b. F/2",
      "c. F",
      "d. 2F/3"
    ],
    "answer": "a"
  },
  {
    "id": 485,
    "q": "Two objects (m and 3m) collide head-on. After collision, m is at rest. What is the coefficient of restitution?",
    "options": [
      "a. 1/3",
      "b. 1",
      "c. 2/3",
      "d. 3"
    ],
    "answer": "a"
  },
  {
    "id": 486,
    "q": "A particle moves on a smooth horizontal surface and is attached to a spring fixed at origin. It is given an initial radial velocity. What is the nature of the subsequent motion?",
    "options": [
      "a. Oscillatory and rotational — the orbit is generally not circular but precesses",
      "b. Simple circular orbit",
      "c. Straight-line SHM",
      "d. Free parabolic motion"
    ],
    "answer": "a"
  },
  {
    "id": 487,
    "q": "A 1 kg block oscillates on a horizontal spring with A = 0.2 m, ω = 5 rad/s. At what position from equilibrium is its instantaneous power delivered by the spring equal to zero?",
    "options": [
      "a. At x = ±A (the turning points)",
      "b. At x = 0",
      "c. At x = A/2",
      "d. Midway between A/2 and A"
    ],
    "answer": "a"
  },
  {
    "id": 488,
    "q": "A hollow ball (I = 2/3 MR²) and a solid ball (I = 2/5 MR²) of equal mass and radius roll without slipping from rest down the same incline. What is the ratio of their speeds at the bottom (v_solid / v_hollow)?",
    "options": [
      "a. √(25/21) ≈ 1.091",
      "b. √(5/3) ≈ 1.29",
      "c. 1",
      "d. √(2/3)"
    ],
    "answer": "a"
  },
  {
    "id": 489,
    "q": "A 3 kg mass is attached to a 2 m string and rotates in a horizontal circle at 4 rad/s on a frictionless table. The string breaks at 96 N. The string is gradually shortened by pulling through a hole. At what length does it break?",
    "options": [
      "a. √(3/2) ≈ 1.22 m",
      "b. 1.0 m",
      "c. 0.5 m",
      "d. 1.5 m"
    ],
    "answer": "a"
  },
  {
    "id": 490,
    "q": "A ball is thrown at 45° from the top of a building 30 m high at 20 m/s. What is the total time of flight? (g = 10 m/s²)",
    "options": [
      "a. ≈ 3.83 s",
      "b. 2 s",
      "c. 4 s",
      "d. 5 s"
    ],
    "answer": "a"
  },
  {
    "id": 491,
    "q": "A 2 kg mass on a string swings as a simple pendulum with length 2.5 m. At the lowest point, its speed is 3 m/s. What is the angle of swing? (g = 10 m/s²)",
    "options": [
      "a. ≈ 25.8°",
      "b. 30°",
      "c. 45°",
      "d. 20°"
    ],
    "answer": "a"
  },
  {
    "id": 492,
    "q": "A 500 g toy car is driven by a compressed spring (k = 80 N/m, compressed 0.1 m). On a horizontal surface (μk = 0.2), how far does the car travel from the release point? (g = 10 m/s²)",
    "options": [
      "a. 0.4 m",
      "b. 0.8 m",
      "c. 0.2 m",
      "d. 1.0 m"
    ],
    "answer": "a"
  },
  {
    "id": 493,
    "q": "A 3 kg particle undergoes SHM: x = 0.4 cos(5t − π/3) m. What is the phase angle at t = 0, and what is the initial velocity?",
    "options": [
      "a. Phase = −π/3; v₀ = 5 × 0.4 × sin(π/3) ≈ 1.73 m/s",
      "b. Phase = π/3; v₀ = 0",
      "c. Phase = 0; v₀ = 2 m/s",
      "d. Phase = π/6; v₀ = 1 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 494,
    "q": "A 6 kg mass is dropped from 20 m onto a spring (k = 12,000 N/m). What is the maximum compression? (g = 10 m/s²; neglect mass of spring)",
    "options": [
      "a. 0.16 m",
      "b. 0.32 m",
      "c. 0.08 m",
      "d. 0.24 m"
    ],
    "answer": "a"
  },
  {
    "id": 495,
    "q": "A uniform disc has moment of inertia I_cm = ½MR² about its centre. What is the moment of inertia about an axis tangent to its rim in the plane of the disc? (parallel axis theorem)",
    "options": [
      "a. 3/2 MR²",
      "b. 5/2 MR²",
      "c. ½MR²",
      "d. 2MR²"
    ],
    "answer": "a"
  },
  {
    "id": 496,
    "q": "A car of mass 1200 kg moves with velocity 20 m/s east. A 800 kg car moves at 15 m/s north. They collide and stick together. What is the kinetic energy lost in collision?",
    "options": [
      "a. ≈ 108,000 J",
      "b. ≈ 54,000 J",
      "c. 0 J",
      "d. ≈ 216,000 J"
    ],
    "answer": "a"
  },
  {
    "id": 497,
    "q": "At what angular velocity must a space station of radius 100 m rotate to simulate Earth gravity? (g = 10 m/s²)",
    "options": [
      "a. 0.316 rad/s",
      "b. 0.1 rad/s",
      "c. 1.0 rad/s",
      "d. 10 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 498,
    "q": "Two springs k₁ = 300 N/m and k₂ = 600 N/m support a 6 kg mass in parallel. What is the frequency of vertical oscillation? (g = 10 m/s²)",
    "options": [
      "a. (√150)/π ≈ 3.90 Hz",
      "b. (√150)/(2π) ≈ 1.95 Hz",
      "c. √150/π² Hz",
      "d. 10 Hz"
    ],
    "answer": "b"
  },
  {
    "id": 499,
    "q": "A 2 kg mass hangs from a spring (k = 200 N/m) at equilibrium. It is given a downward velocity of 2 m/s. What is the amplitude of the resulting oscillation? (g = 10 m/s²)",
    "options": [
      "a. 0.2 m",
      "b. 0.1 m",
      "c. 0.4 m",
      "d. 0.05 m"
    ],
    "answer": "a"
  },
  {
    "id": 500,
    "q": "A 4 kg block slides from rest down a 37° rough incline (μk = 0.2, length = 5 m) and collides with a 2 kg block at the bottom. The collision is elastic. What is the velocity of the 2 kg block after collision? (g = 10 m/s², sin37° = 0.6, cos37° = 0.8)",
    "options": [
      "a. ≈ 6.13 m/s",
      "b. 5.0 m/s",
      "c. 4.0 m/s",
      "d. 8.0 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 501,
    "q": "A satellite of mass m moves from a circular orbit of radius R to radius 2R. How much work must be done by a rocket engine (assume instantaneous burn at each orbit)?",
    "options": [
      "a. GMm/4R",
      "b. GMm/2R",
      "c. GMm/R",
      "d. −GMm/4R"
    ],
    "answer": "a"
  },
  {
    "id": 502,
    "q": "A variable force F = (3x² + 2x) N acts along the x-axis. What is the work done in moving a particle from x = 1 m to x = 3 m?",
    "options": [
      "a. 34 J",
      "b. 28 J",
      "c. 42 J",
      "d. 16 J"
    ],
    "answer": "a"
  },
  {
    "id": 503,
    "q": "A 4 kg block is pushed 6 m up a 30° rough incline (μk = 0.25) by a force parallel to the incline. Using the work-energy theorem, if the block starts and ends at rest, what is the applied force? (g = 10 m/s², sin30° = 0.5, cos30° = 0.866)",
    "options": [
      "a. 28.66 N",
      "b. 20 N",
      "c. 10.66 N",
      "d. 40 N"
    ],
    "answer": "a"
  },
  {
    "id": 504,
    "q": "A 5 kg box starts from rest and is pulled 4 m along a horizontal surface by F = (10 + 2x) N. If μk = 0.2, what is the final kinetic energy? (g = 10 m/s²)",
    "options": [
      "a. 16 J",
      "b. 32 J",
      "c. 56 J",
      "d. 40 J"
    ],
    "answer": "b"
  },
  {
    "id": 505,
    "q": "A 2 kg object is launched vertically upward with KE = 180 J. Using energy conservation, what maximum height does it reach? (g = 10 m/s²)",
    "options": [
      "a. 9 m",
      "b. 18 m",
      "c. 4.5 m",
      "d. 36 m"
    ],
    "answer": "a"
  },
  {
    "id": 506,
    "q": "A car engine provides constant power P = 40 kW. The car has mass 1000 kg and road resistance is 500 N. What is the maximum speed the car can sustain?",
    "options": [
      "a. 80 m/s",
      "b. 40 m/s",
      "c. 20 m/s",
      "d. 160 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 507,
    "q": "A 3 kg mass moves under the influence of a conservative force. Its potential energy is U = 4x² − 8x + 3 J. What is the equilibrium position, and what is the frequency of small oscillations?",
    "options": [
      "a. x = 1 m; f = (1/π)√(8/3) ≈ 0.520 Hz",
      "b. x = 2 m; f = 1 Hz",
      "c. x = 0 m; f = 2 Hz",
      "d. x = 1 m; f = 1/2π Hz"
    ],
    "answer": "a"
  },
  {
    "id": 508,
    "q": "A 10 kg crate is pushed by a horizontal force F along a surface (μk = 0.3) for 5 m, reaching a final speed of 4 m/s from rest. What is F? (g = 10 m/s²)",
    "options": [
      "a. 46 N",
      "b. 30 N",
      "c. 16 N",
      "d. 60 N"
    ],
    "answer": "a"
  },
  {
    "id": 509,
    "q": "A 6 kg solid cylinder (I = ½MR², R = 0.3 m) is initially spinning at ω = 20 rad/s with its axis horizontal. It is placed on a horizontal surface with μk = 0.4. How long before it rolls without slipping? (g = 10 m/s²)",
    "options": [
      "a. 1.33 s",
      "b. 2.0 s",
      "c. 0.67 s",
      "d. 4.0 s"
    ],
    "answer": "a"
  },
  {
    "id": 510,
    "q": "A 4 kg uniform thin rod of length 2 m is free to rotate about a frictionless pin at one end. It falls from a horizontal position. What is the speed of the free end just before it strikes the floor? (g = 10 m/s², I = ML²/3)",
    "options": [
      "a. √(3gL) = √60 ≈ 7.75 m/s",
      "b. √(2gL) ≈ 6.32 m/s",
      "c. √(gL) ≈ 4.47 m/s",
      "d. √(4gL) ≈ 8.94 m/s"
    ],
    "answer": "a"
  },
  {
    "id": 511,
    "q": "A 3 kg disc (I = ½MR², R = 0.2 m) rolls without slipping along a surface and then up a frictionless incline. If its centre-of-mass speed at the base is 5 m/s, what height does it reach?",
    "options": [
      "a. 1.875 m",
      "b. 1.25 m",
      "c. 2.5 m",
      "d. 0.94 m"
    ],
    "answer": "a"
  },
  {
    "id": 512,
    "q": "A 5 kg uniform rod of length 3 m is pinned at one end. It is struck at its centre of percussion (2L/3 from pin) by an impulse of 30 N·s. What is the angular velocity just after the blow?",
    "options": [
      "a. 6 rad/s",
      "b. 3 rad/s",
      "c. 9 rad/s",
      "d. 12 rad/s"
    ],
    "answer": "a"
  },
  {
    "id": 513,
    "q": "A 2 kg particle is acted upon by a force F = (4t − 2) N along the x-axis. It starts from rest. Using the impulse-momentum theorem, what is its velocity at t = 4 s?",
    "options": [
      "a. 12 m/s",
      "b. 6 m/s",
      "c. 24 m/s",
      "d. 8 m/s"
    ],
    "answer": "a"
  }
],


    "Mathematics": 
    [
      {
    "q": "Which set is the subset of all given sets?",
    "options": [
      "{1,2,3}",
      "{1}",
      "{0,1,6,7}",
      "∅"
    ],
    "answer": "∅"
  },
  {
    "q": "A circle whose diameter touches the circumference at the points (−3,6) and (5,4) is represented by the equation",
    "options": [
      "x² + y² + 3x − 2y + 2 = 0",
      "x² + y² − 3x + 4y + 2 = 0",
      "x² + y² − 2x − 10y + 9 = 0",
      "4x² + 4y² − 12x − 20y + 9 = 0"
    ],
    "answer": "x² + y² − 2x − 10y + 9 = 0"
  },
  {
    "q": "The sum of n terms of a certain series is $S_n = 4^n - 1$ for all values of n. Find the average of the first three terms of the series.",
    "options": [
      "20",
      "19",
      "21",
      "18"
    ],
    "answer": "21"
  },
  {
    "q": "Which of the following identities is NOT correct?",
    "options": [
      "$\\sin^2 a = \\frac{1 - \\sin 2a}{2}$",
      "$\\sin^2 a = \\frac{1 - \\cos 2a}{2}$",
      "$\\cos^2 a = \\frac{1 + \\cos 2a}{2}$",
      "$\\sin 2a = 2\\sin a \\cos a$"
    ],
    "answer": "$\\sin^2 a = \\frac{1 - \\sin 2a}{2}$"
  },
  {
    "q": "The constant coefficients of the 5th, 6th and 7th terms in the expansion of $(1+x)^n$ are in AP. Find n.",
    "options": [
      "7",
      "14",
      "12",
      "10"
    ],
    "answer": "14"
  },
  {
    "q": "If $x^2 - 2ax + a^2 = 0$, find the value of $\\frac{x}{a}$.",
    "options": [
      "0",
      "1",
      "3",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "Which of the following is incorrect?",
    "options": [
      "Rational numbers can always be expressed using terminating or repeating decimals.",
      "Rational numbers can be written as quotient of two integers.",
      "Rational numbers are any numbers that can be expressed in the form $\\frac{a}{b}$ where a and b are integers.",
      "The real number system is not made up of a set of rational and irrational numbers."
    ],
    "answer": "The real number system is not made up of a set of rational and irrational numbers."
  },
  {
    "q": "The triangle formed by the vertices of the points (−2, 8), (3, 20) and (11, 8) is a/an",
    "options": [
      "scalene",
      "right angled",
      "isosceles",
      "equilateral"
    ],
    "answer": "isosceles"
  },
  {
    "q": "If $z_1 = 2 + 7i$, $z_2 = 1 + 3i$, then $\\text{Re}(z_1 \\overline{z_2})$ is",
    "options": [
      "1",
      "7i",
      "8",
      "-1"
    ],
    "answer": "23"
  },
  {
    "q": "The sum of the constant coefficients in the expansion of $(1 - x)^{10}$ is",
    "options": [
      "1024",
      "900",
      "0",
      "$10^{10}$"
    ],
    "answer": "0"
  },
  {
    "q": "Find the coordinates of the point P which divides the interval A(−3,−7), B(−1,−4) externally in the ratio 4:3.",
    "options": [
      "(5, 5)",
      "(2, 4)",
      "(−3, −7)",
      "(−7, 11)"
    ],
    "answer": "(5, 5)"
  },
  {
    "q": "The sum of the exponents of x and y in any term of the expansion $(x + y)^n$ is",
    "options": [
      "n",
      "n+1",
      "n−1",
      "n/2"
    ],
    "answer": "n"
  },
  {
    "q": "Given that $z = -3 + 4i$ and $zw = -14 + 2i$. Find the modulus and argument of w.",
    "options": [
      "$2\\sqrt{2}, \\frac{\\pi}{4}$",
      "$4\\sqrt{2}, \\frac{\\pi}{4}$",
      "$4\\sqrt{2}, 4$",
      "$2\\sqrt{2}, 4$"
    ],
    "answer": "$2\\sqrt{2}, \\frac{\\pi}{4}$"
  },
  {
    "q": "Which set is the subset of all given sets?",
    "options": [
      "{1,2,3}",
      "{1}",
      "{0,1,6,7}",
      "∅"
    ],
    "answer": "∅"
  },
  {
    "q": "A circle whose diameter touches the circumference at the points (−3,6) and (5,4) is represented by the equation",
    "options": [
      "x² + y² + 3x − 2y + 2 = 0",
      "x² + y² − 3x + 4y + 2 = 0",
      "x² + y² − 2x − 10y + 9 = 0",
      "4x² + 4y² − 12x − 20y + 9 = 0"
    ],
    "answer": "x² + y² − 2x − 10y + 9 = 0"
  },
  {
    "q": "The sum of n terms of a certain series is $S_n = 4^n - 1$ for all values of n. Find the average of the first three terms of the series.",
    "options": [
      "20",
      "19",
      "21",
      "18"
    ],
    "answer": "21"
  },
  {
    "q": "Which of the following identities is NOT correct?",
    "options": [
      "$\\sin^2 a = \\frac{1 - \\sin 2a}{2}$",
      "$\\sin^2 a = \\frac{1 - \\cos 2a}{2}$",
      "$\\cos^2 a = \\frac{1 + \\cos 2a}{2}$",
      "$\\sin 2a = 2\\sin a \\cos a$"
    ],
    "answer": "$\\sin^2 a = \\frac{1 - \\sin 2a}{2}$"
  },
  {
    "q": "The constant coefficients of the 5th, 6th and 7th terms in the expansion of $(1+x)^n$ are in AP. Find n.",
    "options": [
      "7",
      "14",
      "12",
      "10"
    ],
    "answer": "14"
  },
  {
    "q": "If $x^2 - 2ax + a^2 = 0$, find the value of $\\frac{x}{a}$.",
    "options": [
      "0",
      "1",
      "3",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "Which of the following is incorrect?",
    "options": [
      "Rational numbers can always be expressed using terminating or repeating decimals.",
      "Rational numbers can be written as quotient of two integers.",
      "Rational numbers are any numbers that can be expressed in the form $\\frac{a}{b}$ where a and b are integers.",
      "The real number system is not made up of a set of rational and irrational numbers."
    ],
    "answer": "The real number system is not made up of a set of rational and irrational numbers."
  },
  {
    "q": "The triangle formed by the vertices of the points (−2, 8), (3, 20) and (11, 8) is a/an",
    "options": [
      "scalene",
      "right angled",
      "isosceles",
      "equilateral"
    ],
    "answer": "isosceles"
  },
  {
    "q": "If $z_1 = 2 + 7i$, $z_2 = 1 + 3i$, then $\\text{Re}(z_1 \\overline{z_2})$ is",
    "options": [
      "1",
      "7i",
      "8",
      "-1"
    ],
    "answer": "23"
  },
  {
    "q": "The sum of the constant coefficients in the expansion of $(1 - x)^{10}$ is",
    "options": [
      "1024",
      "900",
      "0",
      "$10^{10}$"
    ],
    "answer": "0"
  },
  {
    "q": "Find the coordinates of the point P which divides the interval A(−3,−7), B(−1,−4) externally in the ratio 4:3.",
    "options": [
      "(5, 5)",
      "(2, 4)",
      "(−3, −7)",
      "(−7, 11)"
    ],
    "answer": "(5, 5)"
  },
  {
    "q": "The sum of the exponents of x and y in any term of the expansion $(x + y)^n$ is",
    "options": [
      "n",
      "n+1",
      "n−1",
      "n/2"
    ],
    "answer": "n"
  },
  {
    "q": "A vertical tower stands on level ground. At a point 100m from the foot of the tower, the angle of elevation of the top is 20°. The height of the tower is:",
    "options": ["36.4m", "34.2m", "40.0m", "32.6m"],
    "answer": "36.4m"
  },
  {
    "q": "$\\frac{3}{4}\\pi$ radian is equivalent to how many degrees?",
    "options": ["90°", "120°", "135°", "150°"],
    "answer": "135°"
  },
  {
    "q": "If $\\tan(t) = 13$, then $\\cot(-t) = ?$",
    "options": ["$\\frac{1}{13}$", "$-\\frac{1}{13}$", "$13$", "$-13$"],
    "answer": "$-\\frac{1}{13}$"
  },
  {
    "q": "Which of the following is NOT correct?",
    "options": [
      "$\\sin(x) = -\\sin(-x)$",
      "$\\sec(-t) = \\sec(t)$",
      "$\\sin(\\pi + x) = \\sin(x)$",
      "$\\cos(\\pi - x) = -\\cos(x)$"
    ],
    "answer": "$\\sin(\\pi + x) = \\sin(x)$"
  },
  {
    "q": "Simplify $\\frac{(\\csc y + \\cot y)(\\csc y - \\cot y)}{\\csc y}$",
    "options": ["$\\cos y$", "$\\sin y$", "$\\tan y$", "$\\cot y$"],
    "answer": "$\\sin y$"
  },
  {
    "q": "Use trigonometric identities to find the exact value of $\\frac{\\tan 40° + \\tan 110°}{1 - \\tan 40° \\tan 110°}$",
    "options": ["$\\frac{\\sqrt{3}}{3}$", "$-\\frac{\\sqrt{3}}{3}$", "$\\sqrt{3}$", "$-\\sqrt{3}$"],
    "answer": "$-\\frac{\\sqrt{3}}{3}$"
  },
  {
    "q": "If $\\tan \\alpha = \\frac{4}{3}$, $\\alpha$ lies in quadrant III, and $\\cos \\beta = -\\frac{20}{29}$, $\\beta$ lies in quadrant II. Find $\\sin(\\alpha + \\beta)$",
    "options": ["0.1167", "0.2134", "-0.1167", "0.5"],
    "answer": "0.1167"
  },
  {
    "q": "The exact value of $\\cos 35° \\cos 25° - \\sin 35° \\sin 25°$ is:",
    "options": ["$\\frac{\\sqrt{3}}{2}$", "$\\frac{1}{2}$", "$\\frac{\\sqrt{2}}{2}$", "$1$"],
    "answer": "$\\frac{1}{2}$"
  },
  {
    "q": "$\\frac{\\cos x + \\sin x}{\\cos x} - \\frac{\\sin x - \\cos x}{\\sin x} = ?$",
    "options": ["$\\sec x \\cdot \\csc x$", "$\\sin x \\cdot \\cos x$", "$\\tan x + \\cot x$", "$1$"],
    "answer": "$\\sec x \\cdot \\csc x$"
  },
  {
    "q": "135° in radians is?",
    "options": ["$\\frac{\\pi}{4}$", "$\\frac{\\pi}{2}$", "$\\frac{3\\pi}{4}$", "$\\frac{2\\pi}{3}$"],
    "answer": "$\\frac{3\\pi}{4}$"
  },
  {
    "q": "The value of $\\frac{\\sin 150° - 5\\cos 300° + 7\\tan 225°}{\\tan 135° + 3\\sin 210°}$ is",
    "options": ["1", "-1", "2", "-2"],
    "answer": "-2"
  },
  {
    "q": "In triangle ABC, right-angled at B, AB = 24 cm, BC = 7 cm. The value of $\\tan C$ is:",
    "options": ["$\\frac{7}{24}$", "$\\frac{24}{7}$", "$\\frac{7}{25}$", "$\\frac{25}{7}$"],
    "answer": "$\\frac{24}{7}$"
  },
  {
    "q": "The value of $\\frac{\\cot 30°}{\\tan 60°}$ is:",
    "options": ["$\\frac{1}{3}$", "$\\sqrt{3}$", "$\\frac{1}{\\sqrt{3}}$", "$1$"],
    "answer": "$1$"
  },
  {
    "q": "If $\\theta$ is an acute angle and $4\\cos^2\\theta - 1 = 0$, then what is the value of $\\tan(\\theta - 15°)$?",
    "options": ["1 or -3.7321", "0 or 1", "$\\sqrt{3}$", "$\\frac{1}{\\sqrt{3}}$"],
    "answer": "1 or -3.7321"
  },
  {
    "q": "If $\\alpha + \\beta = 90°$ and $\\alpha : \\beta = 2:1$, what is the ratio of $\\cos \\alpha$ to $\\cos \\beta$?",
    "options": ["$1:\\sqrt{3}$", "$\\sqrt{3}:3$", "$1:2$", "$\\sqrt{3}:1$"],
    "answer": "$\\sqrt{3}:3$"
  },
  {
    "q": "Find the correct trigonometric identity.",
    "options": [
      "$\\tan^2\\theta = \\sec^2\\theta - 1$",
      "$\\tan^2\\theta + \\sec^2\\theta = 1$",
      "$\\tan^2\\theta - \\sec^2\\theta = 1$",
      "$\\tan^2\\theta = \\sec^2\\theta + 1$"
    ],
    "answer": "$\\tan^2\\theta = \\sec^2\\theta - 1$"
  },
  {
    "q": "Evaluate $(\\csc\\theta - \\cot\\theta)(\\csc\\theta + \\cot\\theta)$",
    "options": ["0", "1", "$\\csc^2\\theta$", "$\\cot^2\\theta$"],
    "answer": "1"
  },
  {
    "q": "Which of the following is NOT the same as $\\tan(t)$?",
    "options": [
      "$\\tan(-t)$",
      "$\\tan(t + 2\\pi)$",
      "$\\tan(t + \\pi)$",
      "$\\tan\\left(t + \\frac{\\pi}{2}\\right)$"
    ],
    "answer": "$\\tan\\left(t + \\frac{\\pi}{2}\\right)$"
  },
  {
    "q": "Simplify $(\\sin^2 x + \\cos^2 x) - (\\csc^2 x - \\cot^2 x)$",
    "options": ["0", "1", "2", "-1"],
    "answer": "0"
  },
  {
    "q": "What is $\\frac{1 - \\cos x}{\\sin x}$?",
    "options": [
      "$\\frac{\\sin x}{1 + \\cos x}$",
      "$\\frac{\\cos x}{1 - \\sin x}$",
      "$\\tan x$",
      "$\\cot x$"
    ],
    "answer": "$\\frac{\\sin x}{1 + \\cos x}$"
  },
  {
    "q": "$\\sin^2 x + \\sin^2 x \\cot^2 x = ?$",
    "options": ["0", "1", "$\\sin^2 x$", "$\\cos^2 x$"],
    "answer": "1"
  },
  {
    "q": "Convert $\\frac{11}{4}\\pi$ to degrees",
    "options": ["360°", "405°", "495°", "450°"],
    "answer": "495°"
  },
  {
    "q": "Value of $\\begin{vmatrix} \\cos 15° & \\sin 15° \\\\ -\\sin 15° & \\cos 15° \\end{vmatrix}$ is:",
    "options": ["0", "1", "-1", "$\\cos 30°$"],
    "answer": "1"
  },
  {
    "q": "An ellipsis is a series of __________.",
    "options": [
      "Three semicolons",
      "Two periods",
      "Three periods",
      "Five periods and a comma"
    ],
    "answer": "Three periods"
  },
  {
    "q": "Which set is the subset of all given sets?",
    "options": [
      "{1,2,3}",
      "{1}",
      "{0,1,6,7}",
      "∅"
    ],
    "answer": "∅"
  },
  {
    "q": "A circle whose diameter touches the circumference at the points (−3,6) and (5,4) is represented by the equation",
    "options": [
      "x² + y² + 3x − 2y + 2 = 0",
      "x² + y² − 3x + 4y + 2 = 0",
      "x² + y² − 2x − 10y + 9 = 0",
      "4x² + 4y² − 12x − 20y + 9 = 0"
    ],
    "answer": "x² + y² − 2x − 10y + 9 = 0"
  },
  {
    "q": "The sum of n terms of a certain series is $S_n = 4^n - 1$ for all values of n. Find the average of the first three terms of the series.",
    "options": [
      "20",
      "19",
      "21",
      "18"
    ],
    "answer": "21"
  },
  {
    "q": "Which of the following identities is NOT correct?",
    "options": [
      "$\\sin^2 a = \\frac{1 - \\sin 2a}{2}$",
      "$\\sin^2 a = \\frac{1 - \\cos 2a}{2}$",
      "$\\cos^2 a = \\frac{1 + \\cos 2a}{2}$",
      "$\\sin 2a = 2\\sin a \\cos a$"
    ],
    "answer": "$\\sin^2 a = \\frac{1 - \\sin 2a}{2}$"
  },
  {
    "q": "The constant coefficients of the 5th, 6th and 7th terms in the expansion of $(1+x)^n$ are in AP. Find n.",
    "options": [
      "7",
      "14",
      "12",
      "10"
    ],
    "answer": "14"
  },
  {
    "q": "If $x^2 - 2ax + a^2 = 0$, find the value of $\\frac{x}{a}$.",
    "options": [
      "0",
      "1",
      "3",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "Which of the following is incorrect?",
    "options": [
      "Rational numbers can always be expressed using terminating or repeating decimals.",
      "Rational numbers can be written as quotient of two integers.",
      "Rational numbers are any numbers that can be expressed in the form $\\frac{a}{b}$ where a and b are integers.",
      "The real number system is not made up of a set of rational and irrational numbers."
    ],
    "answer": "The real number system is not made up of a set of rational and irrational numbers."
  },
  {
    "q": "The triangle formed by the vertices of the points (−2, 8), (3, 20) and (11, 8) is a/an",
    "options": [
      "scalene",
      "right angled",
      "isosceles",
      "equilateral"
    ],
    "answer": "isosceles"
  },
  {
    "q": "If $z_1 = 2 + 7i$, $z_2 = 1 + 3i$, then $\\text{Re}(z_1 \\overline{z_2})$ is",
    "options": [
      "1",
      "7i",
      "8",
      "-1"
    ],
    "answer": "23"
  },
  {
    "q": "The sum of the constant coefficients in the expansion of $(1 - x)^{10}$ is",
    "options": [
      "1024",
      "900",
      "0",
      "$10^{10}$"
    ],
    "answer": "0"
  },
  {
    "q": "Find the coordinates of the point P which divides the interval A(−3,−7), B(−1,−4) externally in the ratio 4:3.",
    "options": [
      "(5, 5)",
      "(2, 4)",
      "(−3, −7)",
      "(−7, 11)"
    ],
    "answer": "(5, 5)"
  },
  {
    "q": "The sum of the exponents of x and y in any term of the expansion $(x + y)^n$ is",
    "options": [
      "n",
      "n+1",
      "n−1",
      "n/2"
    ],
    "answer": "n"
  },
  {
    "q": "Given that $z = -3 + 4i$ and $zw = -14 + 2i$. Find the modulus and argument of w.",
    "options": [
      "$2\\sqrt{2}, \\frac{\\pi}{4}$",
      "$4\\sqrt{2}, \\frac{\\pi}{4}$",
      "$4\\sqrt{2}, 4$",
      "$2\\sqrt{2}, 4$"
    ],
    "answer": "$2\\sqrt{2}, \\frac{\\pi}{4}$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are roots of $2x^2 + 3x - 7 = 0$, find the value of $\\frac{\\beta}{\\alpha} + \\frac{\\alpha}{\\beta}$.",
    "options": [
      "$\\frac{2}{7}$",
      "$\\frac{37}{14}$",
      "$-\\frac{37}{14}$",
      "$\\frac{5}{7}$"
    ],
    "answer": "$-\\frac{37}{14}$"
  },
  {
    "q": "Which of the following equations does NOT represent a circle?",
    "options": [
      "$3x^2 + 3y^2 - 2y = 0$",
      "$x^2 + y^2 - 4x + 6y + 13 = 0$",
      "$x^2 + y^2 = 25$",
      "$2x^2 + y^2 - 3x + y = 0$"
    ],
    "answer": "$2x^2 + y^2 - 3x + y = 0$"
  },
  {
    "q": "If $A = 3 - 2i$ and $B = 1 + 2i$, find the modulus of $\\frac{A}{B}$.",
    "options": [
      "$\\frac{\\sqrt{74}}{2}$",
      "$\\frac{7}{2}$",
      "$\\sqrt{\\frac{13}{5}}$",
      "$\\frac{13}{5}$"
    ],
    "answer": "$\\sqrt{\\frac{13}{5}}$"
  },
  {
    "q": "The sets A and B have 6 and 9 elements respectively, such that A is a proper subset of B. The total number of elements of A union B is",
    "options": [
      "6",
      "9",
      "15",
      "3"
    ],
    "answer": "9"
  },
  {
    "q": "The equation of the normal to the circle $2x^2 + 2y^2 - 4x + 4y = 12$ at the point (−1, 1) is",
    "options": [
      "$x + y - 1 = 0$",
      "$x - y + 2 = 0$",
      "$x + y + 1 = 0$",
      "$x - y - 2 = 0$"
    ],
    "answer": "$x + y + 1 = 0$"
  },
  {
    "q": "Find the distance of the point P(−2, 4) from the line $3x + 4y = 11$.",
    "options": [
      "$\\frac{1}{5}$",
      "$\\frac{2}{5}$",
      "$\\frac{4}{5}$",
      "$\\frac{3}{5}$"
    ],
    "answer": "$\\frac{1}{5}$"
  },
  {
    "q": "If 63% of persons like banana and 76% like apple, what can be said about the percentage of persons who like both banana and apple?",
    "options": [
      "At least 24%",
      "At least 39%",
      "At most 63%",
      "Exactly 50%"
    ],
    "answer": "At least 39%"
  },
  {
    "q": "Find the fourth term of the sequence given that $a_1 = 3$ and $a_{n+1} = 3a_n - 2$.",
    "options": [
      "19",
      "55",
      "25",
      "37"
    ],
    "answer": "55"
  },
  {
    "q": "The sum of the first n terms of a G.P. is 36a. The sum of their reciprocals is $\\frac{36}{a}$. If the first term is 1, find n and the common ratio r.",
    "options": [
      "n=6, r=4",
      "n=6, r=3",
      "n=4, r=6",
      "n=3, r=6"
    ],
    "answer": "n=6, r=3"
  },
  {
    "q": "Given two polynomials $A = 8x^3 - 2x^2 + 5$ and $B = 2x^4 - 2x^3 + 2x^2$. Find $2B - 3A$.",
    "options": [
      "$4x^4 - 26x^3 - 15$",
      "$4x^4 - 8x^2 - 15$",
      "$4x^4 - 36x^3 + 18x^2 - 15$",
      "$4x^4 - 26x^3 + 8x^2 - 15$"
    ],
    "answer": "$4x^4 - 26x^3 + 8x^2 - 15$"
  },
  {
    "q": "The set $A = \\{x : x \\in \\mathbb{N},\\ x^2 - 3x + 2 = 0\\}$ is a",
    "options": [
      "Finite set",
      "Infinite set",
      "Null set",
      "None of these"
    ],
    "answer": "Finite set"
  },
  {
    "q": "Which of the following statement is NOT correct regarding related angles?",
    "options": [
      "If θ is in Q2, its related angle is (180° − θ)",
      "If θ is in Q3, its related angle is obtained by subtracting 180° from θ",
      "The related angle is the positive acute angle between the x-axis and terminal side of θ",
      "None of them"
    ],
    "answer": "None of them"
  },
  {
    "q": "Which of the following conditions is NOT sufficient in deriving the equation of a circle?",
    "options": [
      "A point on the circumference and the coordinate of the center",
      "Two points, one on the circumference and the other outside the circle",
      "Two points as the ends of the diameter",
      "Three points on the circumference"
    ],
    "answer": "Two points, one on the circumference and the other outside the circle"
  },
  {
    "q": "$\\sin^2\\theta + \\cos^2\\theta = ?$",
    "options": [
      "1",
      "0",
      "3",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "Find y if the equation $(5y + 1)x^2 - 8yx + 3y = 0$ has equal roots.",
    "options": [
      "$y \\in (0, 2)$",
      "$y = -\\frac{1}{2}$",
      "$y \\in \\{0, 3\\}$",
      "$y \\in (0, 4)$"
    ],
    "answer": "$y \\in \\{0, 3\\}$"
  },
  {
    "q": "In a group of 300 people, 150 can speak French and 200 can speak German. How many can speak both French and German?",
    "options": [
      "20",
      "50",
      "40",
      "None of these"
    ],
    "answer": "50"
  },
  {
    "q": "The second term of a G.P. is 24 and the fifth term is 81. Find the seventh term.",
    "options": [
      "$\\frac{729}{4}$",
      "$\\frac{243}{2}$",
      "$\\frac{729}{2}$",
      "$\\frac{81}{4}$"
    ],
    "answer": "$\\frac{729}{4}$"
  },
  {
    "q": "The second term of a G.P. is 24 and the sum to infinity is 100. Find the two possible values of the first term and common ratio in the form $(a_1, r_1)$ and $(a_2, r_2)$.",
    "options": [
      "$(4, 2)$ or $(8, 2)$",
      "$(2, 2)$ or $(60, \\frac{1}{2})$",
      "$(20, 2)$ or $(30, \\frac{1}{2})$",
      "$(40, \\frac{3}{5})$ or $(60, \\frac{2}{5})$"
    ],
    "answer": "$(40, \\frac{3}{5})$ or $(60, \\frac{2}{5})$"
  },
  {
    "q": "One of the roots of the equation $x^2 + kx + 15 = 0$ is 3. Find the value of k and the other root.",
    "options": [
      "1, 5",
      "2, 5",
      "5, 2",
      "4, 2"
    ],
    "answer": "2, 5"
  },
  {
    "q": "A G.P. has a common ratio of 2. Find the value of n for which the sum of 2n terms is 33 times the sum of the first n terms.",
    "options": [
      "3",
      "4",
      "5",
      "6"
    ],
    "answer": "5"
  },
  {
    "q": "If n is a positive integer, find the coefficient of $\\frac{1}{x}$ in the expansion of $(1 + x)^n \\left(1 + \\frac{1}{x}\\right)^n$.",
    "options": [
      "$\\binom{2n}{n-1}$",
      "$\\binom{2n}{n}$",
      "$\\binom{n}{n-1}$",
      "$\\binom{2n}{n+1}$"
    ],
    "answer": "$\\binom{2n}{n-1}$"
  },
  {
    "q": "The length of the tangent to the circle $x^2 + y^2 + 3x + 7y + 5 = 0$ at the point (−2, 3) is",
    "options": [
      "$2\\sqrt{33}$ units",
      "$\\sqrt{33}$ units",
      "$33$ units",
      "$\\frac{\\sqrt{33}}{2}$ units"
    ],
    "answer": "$\\sqrt{33}$ units"
  },
  {
    "q": "Write the complex number $z = 2 + 2i$ in polar form $r(\\cos\\theta + i\\sin\\theta)$ with $\\theta$ between 0 and $2\\pi$.",
    "options": [
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} - i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\left(\\cos\\frac{\\pi}{2} + i\\sin\\frac{\\pi}{2}\\right)$",
      "$4\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
    ],
    "answer": "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are the roots of $3x^2 - 5x + 1 = 0$, find $\\alpha^2 + \\beta^2$.",
    "options": [
      "$\\frac{19}{9}$",
      "$\\frac{23}{9}$",
      "$\\frac{5}{3}$",
      "$\\frac{25}{9}$"
    ],
    "answer": "$\\frac{19}{9}$"
  },
  {
    "q": "The radius of the circle $x^2 + y^2 + 6x - 4y - 3 = 0$ is",
    "options": [
      "2",
      "3",
      "4",
      "5"
    ],
    "answer": "4"
  },
  {
    "q": "Evaluate $\\sum_{k=1}^{6} \\frac{5}{k}$",
    "options": [
      "$\\frac{49}{20}$",
      "$\\frac{49}{10}$",
      "$\\frac{29}{20}$",
      "$\\frac{29}{10}$"
    ],
    "answer": "$\\frac{49}{20}$"
  },
  {
    "q": "Solve for k if $10 - 8k + 2k^2 = 0$.",
    "options": [
      "k = 1 or k = 5",
      "k = 2 or k = 5",
      "k = −1 or k = 5",
      "k = 1 or k = −5"
    ],
    "answer": "k = 1 or k = 5"
  },
  {
    "q": "Find the value of $\\int_0^2 4e^{4x} dx$",
    "options": [
      "$e^8 - 1$",
      "$e^8 + 1$",
      "$4(e^8 - 1)$",
      "$e^8$"
    ],
    "answer": "$e^8 - 1$"
  },
  {
    "q": "If $a$ and $b$ are in G.P. and $a^x = b^y = c^z$, find $\\frac{1}{x} + \\frac{1}{z}$ in terms of y.",
    "options": [
      "$\\frac{1}{y}$",
      "$\\frac{2}{y}$",
      "$y$",
      "$\\frac{y}{2}$"
    ],
    "answer": "$\\frac{2}{y}$"
  },
  {
    "q": "Find the radius of the circle $x^2 + y^2 + 6x - 4y = 0$.",
    "options": [
      "$\\sqrt{13}$",
      "$\\sqrt{3}$",
      "$\\sqrt{10}$",
      "$5$"
    ],
    "answer": "$\\sqrt{13}$"
  },
  {
    "q": "Which of the following is incorrect? A. $(x^2 + y^2) = (x+y)^2 - 2xy$  B. $(x^2 + y^2) = (x+y)^2 - 2xy$  C. $\\log_a(\\frac{x}{y}) = \\log_a x - \\log_a y$  D. $\\pi$ is an irrational number",
    "options": [
      "$(x^2 + y^2) \\neq (x+y)^2 - 2xy$ is incorrect",
      "$\\log_a\\left(\\frac{x}{y}\\right) = -\\log_a x$ is incorrect",
      "$\\pi$ is a rational number",
      "None of the above"
    ],
    "answer": "$\\log_a\\left(\\frac{x}{y}\\right) = -\\log_a x$ is incorrect"
  },
  {
    "q": "Find the value of x and y respectively for which the complex equation holds: $(x + iy) = 7 + 9i$",
    "options": [
      "(7, 9)",
      "(9, 7)",
      "(−7, 9)",
      "(7, −9)"
    ],
    "answer": "(7, 9)"
  },
  {
    "q": "Find the length of a line segment formed by the points A(1, 2) and B(4, 6).",
    "options": [
      "3",
      "4",
      "5",
      "6"
    ],
    "answer": "5"
  },
  {
    "q": "Simplify $\\left(\\frac{x^{1/2} + x^{-1/2}}{x^{1/2} - x^{-1/2}}\\right)^2$.",
    "options": [
      "$\\frac{(x+1)^2}{(x-1)^2}$",
      "$\\frac{x+1}{x-1}$",
      "$\\frac{x^2+1}{x^2-1}$",
      "$x$"
    ],
    "answer": "$\\frac{(x+1)^2}{(x-1)^2}$"
  },
  {
    "q": "Which of the following statements about a normal are true EXCEPT",
    "options": [
      "A diameter is normal to the tangent",
      "A normal meets the tangent at a right angle",
      "A normal is a line",
      "A normal is a curve"
    ],
    "answer": "A normal is a curve"
  },
  {
    "q": "Simplify $\\frac{45x^7y^3}{(5xy)^{-2}}$",
    "options": [
      "$\\frac{9}{81y^{-2}}$",
      "$\\frac{25}{4y^2}$",
      "$\\frac{5}{9y^2}$",
      "$\\frac{25x}{81y^{-2}}$"
    ],
    "answer": "$\\frac{25x}{81y^{-2}}$"
  },
  {
    "q": "Find the middle term in the expansion of $(x^2 + y^2)^8$",
    "options": [
      "$\\binom{8}{5}x^5y^3$",
      "$56x^6y^{10}$",
      "$56x^{12}y^6$",
      "$70x^8y^8$"
    ],
    "answer": "$70x^8y^8$"
  },
  {
    "q": "Find the 20th term of an A.P. if the first term is 5 and the common difference is −2.",
    "options": [
      "−33",
      "−29",
      "−31",
      "−27"
    ],
    "answer": "-33"
  },
  {
    "q": "Simplify $\\sin^4\\theta - \\cos^4\\theta$",
    "options": [
      "$\\sin^2\\theta + \\cos^2\\theta$",
      "$\\sin^2\\theta - \\cos^2\\theta$",
      "$1$",
      "$0$"
    ],
    "answer": "$\\sin^2\\theta - \\cos^2\\theta$"
  },
  {
    "q": "One of the roots of the equation $x^2 - kx + 15 = 0$ is 3. The value of k and the other root are respectively",
    "options": [
      "−5, −2",
      "5, 2",
      "3, 5",
      "2, −5"
    ],
    "answer": "−8, 5"
  },
  {
    "q": "Find the value of n if the constant coefficients of the 6th term in the expansion of $\\left(a + \\frac{1}{b}\\right)^n$ are equal.",
    "options": [
      "20",
      "22",
      "16",
      "6"
    ],
    "answer": "20"
  },
  {
    "q": "Find the remainder and the quotient when $2x^3 - 5x^2 + 3x - 5$ is divided by $x^2 + x + 1$",
    "options": [
      "None of the above",
      "$R = 4x - 10,\\ Q = 2x^2 - 6x + 5$",
      "$R = 4x + 10,\\ Q = 2x^2 - 3x + 5$",
      "$Q = 4x - 10,\\ R = 2x^2 - 6x + 5$"
    ],
    "answer": "$R = 4x - 10,\\ Q = 2x^2 - 6x + 5$"
  },
  {
    "q": "The fifth term in the fifth level of Pascal's triangle is",
    "options": [
      "6",
      "1",
      "10",
      "5"
    ],
    "answer": "5"
  },
  {
    "q": "Simplify $m^3 - 2m^2 - m + 2$",
    "options": [
      "$(m^2 + 1)(m + 2)$",
      "$(m^2 + 1)(m - 2)$",
      "$(m^2 - 1)(m - 2)$",
      "$(m - 2)(m + 1)(m - 1)$"
    ],
    "answer": "$(m - 2)(m + 1)(m - 1)$"
  },
  {
    "q": "Evaluate $\\sum_{k=1}^{3} \\frac{k}{k+1}$",
    "options": [
      "$\\frac{47}{12}$",
      "$\\frac{47}{24}$",
      "$\\frac{47}{6}$",
      "$2$"
    ],
    "answer": "$\\frac{47}{24}$"
  },
  {
    "q": "The constant coefficient of the 5th, 6th and 7th term in the expansion of $(1+x)^n$ are in an A.P. Find n.",
    "options": [
      "15",
      "8",
      "11",
      "7"
    ],
    "answer": "7"
  },
  {
    "q": "Find the equation of the line whose x and y intercepts are 2 and $\\frac{2}{5}$ respectively.",
    "options": [
      "$2x - 5y = 2$",
      "$3x + 5y = 2$",
      "$x - 5y = 2$",
      "$x + 5y = 2$"
    ],
    "answer": "$x + 5y = 2$"
  },
  {
    "q": "Which of the following is NOT true?",
    "options": [
      "$\\frac{1}{\\sqrt{3}}(\\cos 60°) = \\sin 60°$",
      "$-(\\tan 60°) = \\tan 30°$",
      "$\\sqrt{3}(\\cos 60°) = \\cos 30°$",
      "$\\sqrt{3}(\\sin 30°) = \\cos 60°$"
    ],
    "answer": "$\\sqrt{3}(\\sin 30°) = \\cos 60°$"
  },
  {
    "q": "Find the values of x and y in the equation $x(1+i)^2 + y(2-i)^2 = 3 + 10i,\\ x, y \\in \\mathbb{R}$",
    "options": [
      "$x = 7,\\ y = 1$",
      "$x = -7,\\ y = -1$",
      "$x = 1,\\ y = 7$",
      "$x = -7,\\ y = 1$"
    ],
    "answer": "$x = 1,\\ y = 7$"
  },
  {
    "q": "The equation of the normal to the circle $2x^2 + 2y^2 - 4x + 4y = 12$ at the point $(−1, 1)$ is",
    "options": [
      "$x + y + 1 = 0$",
      "$x + y - 1 = 0$",
      "$x + y = 0$",
      "$x - y - 1 = 0$"
    ],
    "answer": "$x + y + 1 = 0$"
  },
  {
    "q": "Evaluate $\\frac{2^3 - 1}{3^2 - 2}$",
    "options": [
      "$\\frac{1}{10}$",
      "$0$",
      "$\\frac{10}{9}$",
      "Undefined"
    ],
    "answer": "$1$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are roots of $3x^2 - 5x + 1 = 0$, find $\\alpha^2 - \\beta^2$.",
    "options": [
      "$\\frac{5\\sqrt{13}}{9}$",
      "$\\frac{5\\sqrt{13}}{3}$",
      "$\\frac{\\sqrt{13}}{9}$",
      "$\\frac{\\sqrt{13}}{3}$"
    ],
    "answer": "$\\frac{5\\sqrt{13}}{9}$"
  },
  {
    "q": "Find the length of a line segment formed by the points $A(a-b,\\ a+b)$ and $B(a+b,\\ a-b)$.",
    "options": [
      "$\\sqrt{(a-b)}$",
      "$a + b$",
      "$2ab$",
      "$2\\sqrt{2}b$"
    ],
    "answer": "$2\\sqrt{2}b$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are roots of $2x^2 + 3x - 7 = 0$, find $\\frac{\\alpha}{\\beta^2} + \\frac{\\beta}{\\alpha^2}$.",
    "options": [
      "$\\frac{-153}{56}$",
      "$\\frac{153}{56}$",
      "$\\frac{-153}{28}$",
      "$\\frac{153}{28}$"
    ],
    "answer": "$\\frac{-153}{56}$"
  },
  {
    "q": "The coordinate of the center of a circle with parametric equations $y + 5 = 7\\sin\\theta$ and $x - 6 = 7\\cos\\theta$ is",
    "options": [
      "$(6, 5)$",
      "$(-5, 6)$",
      "$(-6, 5)$",
      "$(6, -5)$"
    ],
    "answer": "$(6, -5)$"
  },
  {
    "q": "Find the value of $\\int_a^b 2x\\,dx$",
    "options": [
      "$b - a$",
      "$b^2 - a^2$",
      "$b^2 + a^2$",
      "$2(b - a)$"
    ],
    "answer": "$b^2 - a^2$"
  },
  {
    "q": "Find the equation of the line parallel to the x-axis which passes through the point of intersection of the lines $4x + 3y - 6 = 0$ and $x - 2y - 7 = 0$.",
    "options": [
      "$2x + 3y = 2$",
      "$y = -3$",
      "$y = 3$",
      "$x = 3$"
    ],
    "answer": "$y = -3$"
  },
  {
    "q": "Evaluate $\\sum_{k=1}^{n} \\frac{1}{k(k+1)}$",
    "options": [
      "$\\frac{n}{n+1}$",
      "$\\frac{2n-1}{n}$",
      "$\\frac{2n-1}{1}$",
      "$\\frac{1}{n+1}$"
    ],
    "answer": "$\\frac{n}{n+1}$"
  },
  {
    "q": "Find the fourth term of the sequence given that $a_1 = 5$ and $a_{n+1} = 5a_n - 2$.",
    "options": [
      "73",
      "313",
      "1563",
      "23"
    ],
    "answer": "313"
  },
  {
    "q": "If $n$ is a positive integer, find the coefficient of $\\frac{1}{x}$ in the expansion of $(1+x)^n\\left(1 + \\frac{1}{x}\\right)^n$.",
    "options": [
      "$\\binom{2n}{n+1}$",
      "$\\binom{2n}{n}$",
      "$\\binom{n}{n-1}$",
      "$\\binom{2n}{n-1}$"
    ],
    "answer": "$\\binom{2n}{n-1}$"
  },
  {
    "q": "Simplify $\\left(\\frac{45x^7y^3}{(5xy)^{-2}}\\right)$",
    "options": [
      "$\\frac{9}{81y^{-2}}$",
      "$\\frac{25}{4y^2}$",
      "$\\frac{5}{9y^2}$",
      "$\\frac{25x}{81y^{-2}}$"
    ],
    "answer": "$\\frac{25x}{81y^{-2}}$"
  },
  {
    "q": "Find the values of x and y respectively for which the equation $x(1+i)^2 + y(2-i)^2 = 3 + 10i$ holds.",
    "options": [
      "$x=7, y=1$",
      "$x=-7, y=-1$",
      "$x=1, y=7$",
      "$x=-7, y=1$"
    ],
    "answer": "$x=1, y=7$"
  },
  {
    "q": "Write the complex number $z = 2 + 2i$ in polar form $r(\\cos\\theta + i\\sin\\theta)$ with $\\theta$ between $0$ and $\\pi$.",
    "options": [
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} - i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\sqrt{2}\\left(\\cos\\frac{3\\pi}{4} + i\\sin\\frac{3\\pi}{4}\\right)$",
      "$2\\sqrt{2}\\left(\\cos\\frac{3\\pi}{4} - i\\sin\\frac{3\\pi}{4}\\right)$"
    ],
    "answer": "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
  },
  {
    "q": "Find the value of $\\frac{2}{3^2 - 1}$",
    "options": [
      "$\\frac{1}{4}$",
      "$0$",
      "$\\frac{10}{9}$",
      "Undefined"
    ],
    "answer": "$\\frac{1}{4}$"
  },
  {
    "q": "Find the modulus of $\\frac{A}{B}$ where $A = 3 - 2i$ and $B = 1 + 2i$.",
    "options": [
      "$\\sqrt{47}$",
      "$\\frac{\\sqrt{13}}{\\sqrt{5}}$",
      "$\\sqrt{74}$",
      "$\\frac{\\sqrt{4}}{7}$"
    ],
    "answer": "$\\frac{\\sqrt{13}}{\\sqrt{5}}$"
  },
  {
    "q": "The sum of the first $n$ terms of a G.P. is 364. The sum of their reciprocals is $\\frac{364}{729}$. If the first term is 1, find $n$ and the common ratio $r$.",
    "options": [
      "$n=6, r=4$",
      "$n=6, r=3$",
      "$n=4, r=6$",
      "$n=3, r=6$"
    ],
    "answer": "$n=6, r=3$"
  },
  {
    "q": "Given that $z = -3 + 4i$ and $zw = -14 + 2i$. Find the modulus and argument of w.",
    "options": [
      "$2\\sqrt{2}, \\frac{\\pi}{4}$",
      "$4\\sqrt{2}, \\frac{\\pi}{4}$",
      "$4\\sqrt{2}, 4$",
      "$2\\sqrt{2}, 4$"
    ],
    "answer": "$2\\sqrt{2}, \\frac{\\pi}{4}$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are roots of $2x^2 + 3x - 7 = 0$, find the value of $\\frac{\\beta}{\\alpha} + \\frac{\\alpha}{\\beta}$.",
    "options": [
      "$\\frac{2}{7}$",
      "$\\frac{37}{14}$",
      "$-\\frac{37}{14}$",
      "$\\frac{5}{7}$"
    ],
    "answer": "$-\\frac{37}{14}$"
  },
  {
    "q": "Which of the following equations does NOT represent a circle?",
    "options": [
      "$3x^2 + 3y^2 - 2y = 0$",
      "$x^2 + y^2 - 4x + 6y + 13 = 0$",
      "$x^2 + y^2 = 25$",
      "$2x^2 + y^2 - 3x + y = 0$"
    ],
    "answer": "$2x^2 + y^2 - 3x + y = 0$"
  },
  {
    "q": "If $A = 3 - 2i$ and $B = 1 + 2i$, find the modulus of $\\frac{A}{B}$.",
    "options": [
      "$\\frac{\\sqrt{74}}{2}$",
      "$\\frac{7}{2}$",
      "$\\sqrt{\\frac{13}{5}}$",
      "$\\frac{13}{5}$"
    ],
    "answer": "$\\sqrt{\\frac{13}{5}}$"
  },
  {
    "q": "The sets A and B have 6 and 9 elements respectively, such that A is a proper subset of B. The total number of elements of A union B is",
    "options": [
      "6",
      "9",
      "15",
      "3"
    ],
    "answer": "9"
  },
  {
    "q": "The equation of the normal to the circle $2x^2 + 2y^2 - 4x + 4y = 12$ at the point (−1, 1) is",
    "options": [
      "$x + y - 1 = 0$",
      "$x - y + 2 = 0$",
      "$x + y + 1 = 0$",
      "$x - y - 2 = 0$"
    ],
    "answer": "$x + y + 1 = 0$"
  },
  {
    "q": "Find the distance of the point P(−2, 4) from the line $3x + 4y = 11$.",
    "options": [
      "$\\frac{1}{5}$",
      "$\\frac{2}{5}$",
      "$\\frac{4}{5}$",
      "$\\frac{3}{5}$"
    ],
    "answer": "$\\frac{1}{5}$"
  },
  {
    "q": "If 63% of persons like banana and 76% like apple, what can be said about the percentage of persons who like both banana and apple?",
    "options": [
      "At least 24%",
      "At least 39%",
      "At most 63%",
      "Exactly 50%"
    ],
    "answer": "At least 39%"
  },
  {
    "q": "Find the fourth term of the sequence given that $a_1 = 3$ and $a_{n+1} = 3a_n - 2$.",
    "options": [
      "19",
      "55",
      "25",
      "37"
    ],
    "answer": "55"
  },
  {
    "q": "The sum of the first n terms of a G.P. is 36a. The sum of their reciprocals is $\\frac{36}{a}$. If the first term is 1, find n and the common ratio r.",
    "options": [
      "n=6, r=4",
      "n=6, r=3",
      "n=4, r=6",
      "n=3, r=6"
    ],
    "answer": "n=6, r=3"
  },
  {
    "q": "Given two polynomials $A = 8x^3 - 2x^2 + 5$ and $B = 2x^4 - 2x^3 + 2x^2$. Find $2B - 3A$.",
    "options": [
      "$4x^4 - 26x^3 - 15$",
      "$4x^4 - 8x^2 - 15$",
      "$4x^4 - 36x^3 + 18x^2 - 15$",
      "$4x^4 - 26x^3 + 8x^2 - 15$"
    ],
    "answer": "$4x^4 - 26x^3 + 8x^2 - 15$"
  },
  {
    "q": "The set $A = \\{x : x \\in \\mathbb{N},\\ x^2 - 3x + 2 = 0\\}$ is a",
    "options": [
      "Finite set",
      "Infinite set",
      "Null set",
      "None of these"
    ],
    "answer": "Finite set"
  },
  {
    "q": "Which of the following statement is NOT correct regarding related angles?",
    "options": [
      "If θ is in Q2, its related angle is (180° − θ)",
      "If θ is in Q3, its related angle is obtained by subtracting 180° from θ",
      "The related angle is the positive acute angle between the x-axis and terminal side of θ",
      "None of them"
    ],
    "answer": "None of them"
  },
  {
    "q": "Which of the following conditions is NOT sufficient in deriving the equation of a circle?",
    "options": [
      "A point on the circumference and the coordinate of the center",
      "Two points, one on the circumference and the other outside the circle",
      "Two points as the ends of the diameter",
      "Three points on the circumference"
    ],
    "answer": "Two points, one on the circumference and the other outside the circle"
  },
  {
    "q": "$\\sin^2\\theta + \\cos^2\\theta = ?$",
    "options": [
      "1",
      "0",
      "3",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "Find y if the equation $(5y + 1)x^2 - 8yx + 3y = 0$ has equal roots.",
    "options": [
      "$y \\in (0, 2)$",
      "$y = -\\frac{1}{2}$",
      "$y \\in \\{0, 3\\}$",
      "$y \\in (0, 4)$"
    ],
    "answer": "$y \\in \\{0, 3\\}$"
  },
  {
    "q": "In a group of 300 people, 150 can speak French and 200 can speak German. How many can speak both French and German?",
    "options": [
      "20",
      "50",
      "40",
      "None of these"
    ],
    "answer": "50"
  },
  {
    "q": "The second term of a G.P. is 24 and the fifth term is 81. Find the seventh term.",
    "options": [
      "$\\frac{729}{4}$",
      "$\\frac{243}{2}$",
      "$\\frac{729}{2}$",
      "$\\frac{81}{4}$"
    ],
    "answer": "$\\frac{729}{4}$"
  },
  {
    "q": "The second term of a G.P. is 24 and the sum to infinity is 100. Find the two possible values of the first term and common ratio in the form $(a_1, r_1)$ and $(a_2, r_2)$.",
    "options": [
      "$(4, 2)$ or $(8, 2)$",
      "$(2, 2)$ or $(60, \\frac{1}{2})$",
      "$(20, 2)$ or $(30, \\frac{1}{2})$",
      "$(40, \\frac{3}{5})$ or $(60, \\frac{2}{5})$"
    ],
    "answer": "$(40, \\frac{3}{5})$ or $(60, \\frac{2}{5})$"
  },
  {
    "q": "One of the roots of the equation $x^2 + kx + 15 = 0$ is 3. Find the value of k and the other root.",
    "options": [
      "1, 5",
      "2, 5",
      "5, 2",
      "4, 2"
    ],
    "answer": "2, 5"
  },
  {
    "q": "A G.P. has a common ratio of 2. Find the value of n for which the sum of 2n terms is 33 times the sum of the first n terms.",
    "options": [
      "3",
      "4",
      "5",
      "6"
    ],
    "answer": "5"
  },
  {
    "q": "If n is a positive integer, find the coefficient of $\\frac{1}{x}$ in the expansion of $(1 + x)^n \\left(1 + \\frac{1}{x}\\right)^n$.",
    "options": [
      "$\\binom{2n}{n-1}$",
      "$\\binom{2n}{n}$",
      "$\\binom{n}{n-1}$",
      "$\\binom{2n}{n+1}$"
    ],
    "answer": "$\\binom{2n}{n-1}$"
  },
  {
    "q": "The length of the tangent to the circle $x^2 + y^2 + 3x + 7y + 5 = 0$ at the point (−2, 3) is",
    "options": [
      "$2\\sqrt{33}$ units",
      "$\\sqrt{33}$ units",
      "$33$ units",
      "$\\frac{\\sqrt{33}}{2}$ units"
    ],
    "answer": "$\\sqrt{33}$ units"
  },
  {
    "q": "Write the complex number $z = 2 + 2i$ in polar form $r(\\cos\\theta + i\\sin\\theta)$ with $\\theta$ between 0 and $2\\pi$.",
    "options": [
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} - i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\left(\\cos\\frac{\\pi}{2} + i\\sin\\frac{\\pi}{2}\\right)$",
      "$4\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
    ],
    "answer": "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are the roots of $3x^2 - 5x + 1 = 0$, find $\\alpha^2 + \\beta^2$.",
    "options": [
      "$\\frac{19}{9}$",
      "$\\frac{23}{9}$",
      "$\\frac{5}{3}$",
      "$\\frac{25}{9}$"
    ],
    "answer": "$\\frac{19}{9}$"
  },
  {
    "q": "The radius of the circle $x^2 + y^2 + 6x - 4y - 3 = 0$ is",
    "options": [
      "2",
      "3",
      "4",
      "5"
    ],
    "answer": "4"
  },
  {
    "q": "Evaluate $\\sum_{k=1}^{6} \\frac{5}{k}$",
    "options": [
      "$\\frac{49}{20}$",
      "$\\frac{49}{10}$",
      "$\\frac{29}{20}$",
      "$\\frac{29}{10}$"
    ],
    "answer": "$\\frac{49}{20}$"
  },
  {
    "q": "Solve for k if $10 - 8k + 2k^2 = 0$.",
    "options": [
      "k = 1 or k = 5",
      "k = 2 or k = 5",
      "k = −1 or k = 5",
      "k = 1 or k = −5"
    ],
    "answer": "k = 1 or k = 5"
  },
  {
    "q": "Find the value of $\\int_0^2 4e^{4x} dx$",
    "options": [
      "$e^8 - 1$",
      "$e^8 + 1$",
      "$4(e^8 - 1)$",
      "$e^8$"
    ],
    "answer": "$e^8 - 1$"
  },
  {
    "q": "If $a$ and $b$ are in G.P. and $a^x = b^y = c^z$, find $\\frac{1}{x} + \\frac{1}{z}$ in terms of y.",
    "options": [
      "$\\frac{1}{y}$",
      "$\\frac{2}{y}$",
      "$y$",
      "$\\frac{y}{2}$"
    ],
    "answer": "$\\frac{2}{y}$"
  },
  {
    "q": "Find the radius of the circle $x^2 + y^2 + 6x - 4y = 0$.",
    "options": [
      "$\\sqrt{13}$",
      "$\\sqrt{3}$",
      "$\\sqrt{10}$",
      "$5$"
    ],
    "answer": "$\\sqrt{13}$"
  },
  {
    "q": "Which of the following is incorrect? A. $(x^2 + y^2) = (x+y)^2 - 2xy$  B. $(x^2 + y^2) = (x+y)^2 - 2xy$  C. $\\log_a(\\frac{x}{y}) = \\log_a x - \\log_a y$  D. $\\pi$ is an irrational number",
    "options": [
      "$(x^2 + y^2) \\neq (x+y)^2 - 2xy$ is incorrect",
      "$\\log_a\\left(\\frac{x}{y}\\right) = -\\log_a x$ is incorrect",
      "$\\pi$ is a rational number",
      "None of the above"
    ],
    "answer": "$\\log_a\\left(\\frac{x}{y}\\right) = -\\log_a x$ is incorrect"
  },
  {
    "q": "Find the value of x and y respectively for which the complex equation holds: $(x + iy) = 7 + 9i$",
    "options": [
      "(7, 9)",
      "(9, 7)",
      "(−7, 9)",
      "(7, −9)"
    ],
    "answer": "(7, 9)"
  },
  {
    "q": "Find the length of a line segment formed by the points A(1, 2) and B(4, 6).",
    "options": [
      "3",
      "4",
      "5",
      "6"
    ],
    "answer": "5"
  },
  {
    "q": "Simplify $\\left(\\frac{x^{1/2} + x^{-1/2}}{x^{1/2} - x^{-1/2}}\\right)^2$.",
    "options": [
      "$\\frac{(x+1)^2}{(x-1)^2}$",
      "$\\frac{x+1}{x-1}$",
      "$\\frac{x^2+1}{x^2-1}$",
      "$x$"
    ],
    "answer": "$\\frac{(x+1)^2}{(x-1)^2}$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are roots of $2x^2 + 3x - 7 = 0$, find the value of $\\frac{\\beta}{\\alpha} + \\frac{\\alpha}{\\beta}$.",
    "options": [
      "$\\frac{2}{7}$",
      "$\\frac{37}{14}$",
      "$-\\frac{37}{14}$",
      "$\\frac{5}{7}$"
    ],
    "answer": "$-\\frac{37}{14}$"
  },
  {
    "q": "Which of the following equations does NOT represent a circle?",
    "options": [
      "$3x^2 + 3y^2 - 2y = 0$",
      "$x^2 + y^2 - 4x + 6y + 13 = 0$",
      "$x^2 + y^2 = 25$",
      "$2x^2 + y^2 - 3x + y = 0$"
    ],
    "answer": "$2x^2 + y^2 - 3x + y = 0$"
  },
  {
    "q": "If $A = 3 - 2i$ and $B = 1 + 2i$, find the modulus of $\\frac{A}{B}$.",
    "options": [
      "$\\frac{\\sqrt{74}}{2}$",
      "$\\frac{7}{2}$",
      "$\\sqrt{\\frac{13}{5}}$",
      "$\\frac{13}{5}$"
    ],
    "answer": "$\\sqrt{\\frac{13}{5}}$"
  },
  {
    "q": "The sets A and B have 6 and 9 elements respectively, such that A is a proper subset of B. The total number of elements of A union B is",
    "options": [
      "6",
      "9",
      "15",
      "3"
    ],
    "answer": "9"
  },
  {
    "q": "The equation of the normal to the circle $2x^2 + 2y^2 - 4x + 4y = 12$ at the point (−1, 1) is",
    "options": [
      "$x + y - 1 = 0$",
      "$x - y + 2 = 0$",
      "$x + y + 1 = 0$",
      "$x - y - 2 = 0$"
    ],
    "answer": "$x + y + 1 = 0$"
  },
  {
    "q": "Find the distance of the point P(−2, 4) from the line $3x + 4y = 11$.",
    "options": [
      "$\\frac{1}{5}$",
      "$\\frac{2}{5}$",
      "$\\frac{4}{5}$",
      "$\\frac{3}{5}$"
    ],
    "answer": "$\\frac{1}{5}$"
  },
  {
    "q": "If 63% of persons like banana and 76% like apple, what can be said about the percentage of persons who like both banana and apple?",
    "options": [
      "At least 24%",
      "At least 39%",
      "At most 63%",
      "Exactly 50%"
    ],
    "answer": "At least 39%"
  },
  {
    "q": "Find the fourth term of the sequence given that $a_1 = 3$ and $a_{n+1} = 3a_n - 2$.",
    "options": [
      "19",
      "55",
      "25",
      "37"
    ],
    "answer": "55"
  },
  {
    "q": "The sum of the first n terms of a G.P. is 36a. The sum of their reciprocals is $\\frac{36}{a}$. If the first term is 1, find n and the common ratio r.",
    "options": [
      "n=6, r=4",
      "n=6, r=3",
      "n=4, r=6",
      "n=3, r=6"
    ],
    "answer": "n=6, r=3"
  },
  {
    "q": "Given two polynomials $A = 8x^3 - 2x^2 + 5$ and $B = 2x^4 - 2x^3 + 2x^2$. Find $2B - 3A$.",
    "options": [
      "$4x^4 - 26x^3 - 15$",
      "$4x^4 - 8x^2 - 15$",
      "$4x^4 - 36x^3 + 18x^2 - 15$",
      "$4x^4 - 26x^3 + 8x^2 - 15$"
    ],
    "answer": "$4x^4 - 26x^3 + 8x^2 - 15$"
  },
  {
    "q": "The set $A = \\{x : x \\in \\mathbb{N},\\ x^2 - 3x + 2 = 0\\}$ is a",
    "options": [
      "Finite set",
      "Infinite set",
      "Null set",
      "None of these"
    ],
    "answer": "Finite set"
  },
  {
    "q": "Which of the following statement is NOT correct regarding related angles?",
    "options": [
      "If θ is in Q2, its related angle is (180° − θ)",
      "If θ is in Q3, its related angle is obtained by subtracting 180° from θ",
      "The related angle is the positive acute angle between the x-axis and terminal side of θ",
      "None of them"
    ],
    "answer": "None of them"
  },
  {
    "q": "Which of the following conditions is NOT sufficient in deriving the equation of a circle?",
    "options": [
      "A point on the circumference and the coordinate of the center",
      "Two points, one on the circumference and the other outside the circle",
      "Two points as the ends of the diameter",
      "Three points on the circumference"
    ],
    "answer": "Two points, one on the circumference and the other outside the circle"
  },
  {
    "q": "$\\sin^2\\theta + \\cos^2\\theta = ?$",
    "options": [
      "1",
      "0",
      "3",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "Find y if the equation $(5y + 1)x^2 - 8yx + 3y = 0$ has equal roots.",
    "options": [
      "$y \\in (0, 2)$",
      "$y = -\\frac{1}{2}$",
      "$y \\in \\{0, 3\\}$",
      "$y \\in (0, 4)$"
    ],
    "answer": "$y \\in \\{0, 3\\}$"
  },
  {
    "q": "In a group of 300 people, 150 can speak French and 200 can speak German. How many can speak both French and German?",
    "options": [
      "20",
      "50",
      "40",
      "None of these"
    ],
    "answer": "50"
  },
  {
    "q": "The second term of a G.P. is 24 and the fifth term is 81. Find the seventh term.",
    "options": [
      "$\\frac{729}{4}$",
      "$\\frac{243}{2}$",
      "$\\frac{729}{2}$",
      "$\\frac{81}{4}$"
    ],
    "answer": "$\\frac{729}{4}$"
  },
  {
    "q": "The second term of a G.P. is 24 and the sum to infinity is 100. Find the two possible values of the first term and common ratio in the form $(a_1, r_1)$ and $(a_2, r_2)$.",
    "options": [
      "$(4, 2)$ or $(8, 2)$",
      "$(2, 2)$ or $(60, \\frac{1}{2})$",
      "$(20, 2)$ or $(30, \\frac{1}{2})$",
      "$(40, \\frac{3}{5})$ or $(60, \\frac{2}{5})$"
    ],
    "answer": "$(40, \\frac{3}{5})$ or $(60, \\frac{2}{5})$"
  },
  {
    "q": "One of the roots of the equation $x^2 + kx + 15 = 0$ is 3. Find the value of k and the other root.",
    "options": [
      "1, 5",
      "2, 5",
      "5, 2",
      "4, 2"
    ],
    "answer": "2, 5"
  },
  {
    "q": "A G.P. has a common ratio of 2. Find the value of n for which the sum of 2n terms is 33 times the sum of the first n terms.",
    "options": [
      "3",
      "4",
      "5",
      "6"
    ],
    "answer": "5"
  },
  {
    "q": "If n is a positive integer, find the coefficient of $\\frac{1}{x}$ in the expansion of $(1 + x)^n \\left(1 + \\frac{1}{x}\\right)^n$.",
    "options": [
      "$\\binom{2n}{n-1}$",
      "$\\binom{2n}{n}$",
      "$\\binom{n}{n-1}$",
      "$\\binom{2n}{n+1}$"
    ],
    "answer": "$\\binom{2n}{n-1}$"
  },
  {
    "q": "The length of the tangent to the circle $x^2 + y^2 + 3x + 7y + 5 = 0$ at the point (−2, 3) is",
    "options": [
      "$2\\sqrt{33}$ units",
      "$\\sqrt{33}$ units",
      "$33$ units",
      "$\\frac{\\sqrt{33}}{2}$ units"
    ],
    "answer": "$\\sqrt{33}$ units"
  },
  {
    "q": "Write the complex number $z = 2 + 2i$ in polar form $r(\\cos\\theta + i\\sin\\theta)$ with $\\theta$ between 0 and $2\\pi$.",
    "options": [
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} - i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$",
      "$2\\left(\\cos\\frac{\\pi}{2} + i\\sin\\frac{\\pi}{2}\\right)$",
      "$4\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
    ],
    "answer": "$2\\sqrt{2}\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$"
  },
  {
    "q": "If $\\alpha$ and $\\beta$ are the roots of $3x^2 - 5x + 1 = 0$, find $\\alpha^2 + \\beta^2$.",
    "options": [
      "$\\frac{19}{9}$",
      "$\\frac{23}{9}$",
      "$\\frac{5}{3}$",
      "$\\frac{25}{9}$"
    ],
    "answer": "$\\frac{19}{9}$"
  },
  {
    "q": "The radius of the circle $x^2 + y^2 + 6x - 4y - 3 = 0$ is",
    "options": [
      "2",
      "3",
      "4",
      "5"
    ],
    "answer": "4"
  },
  {
    "q": "Evaluate $\\sum_{k=1}^{6} \\frac{5}{k}$",
    "options": [
      "$\\frac{49}{20}$",
      "$\\frac{49}{10}$",
      "$\\frac{29}{20}$",
      "$\\frac{29}{10}$"
    ],
    "answer": "$\\frac{49}{20}$"
  },
  {
    "q": "Solve for k if $10 - 8k + 2k^2 = 0$.",
    "options": [
      "k = 1 or k = 5",
      "k = 2 or k = 5",
      "k = −1 or k = 5",
      "k = 1 or k = −5"
    ],
    "answer": "k = 1 or k = 5"
  },
  {
    "q": "Find the value of $\\int_0^2 4e^{4x} dx$",
    "options": [
      "$e^8 - 1$",
      "$e^8 + 1$",
      "$4(e^8 - 1)$",
      "$e^8$"
    ],
    "answer": "$e^8 - 1$"
  },
  {
    "q": "If $a$ and $b$ are in G.P. and $a^x = b^y = c^z$, find $\\frac{1}{x} + \\frac{1}{z}$ in terms of y.",
    "options": [
      "$\\frac{1}{y}$",
      "$\\frac{2}{y}$",
      "$y$",
      "$\\frac{y}{2}$"
    ],
    "answer": "$\\frac{2}{y}$"
  },
  {
    "q": "Find the radius of the circle $x^2 + y^2 + 6x - 4y = 0$.",
    "options": [
      "$\\sqrt{13}$",
      "$\\sqrt{3}$",
      "$\\sqrt{10}$",
      "$5$"
    ],
    "answer": "$\\sqrt{13}$"
  },
  {
    "q": "Which of the following is incorrect? A. $(x^2 + y^2) = (x+y)^2 - 2xy$  B. $(x^2 + y^2) = (x+y)^2 - 2xy$  C. $\\log_a(\\frac{x}{y}) = \\log_a x - \\log_a y$  D. $\\pi$ is an irrational number",
    "options": [
      "$(x^2 + y^2) \\neq (x+y)^2 - 2xy$ is incorrect",
      "$\\log_a\\left(\\frac{x}{y}\\right) = -\\log_a x$ is incorrect",
      "$\\pi$ is a rational number",
      "None of the above"
    ],
    "answer": "$\\log_a\\left(\\frac{x}{y}\\right) = -\\log_a x$ is incorrect"
  },
  {
    "q": "Find the value of x and y respectively for which the complex equation holds: $(x + iy) = 7 + 9i$",
    "options": [
      "(7, 9)",
      "(9, 7)",
      "(−7, 9)",
      "(7, −9)"
    ],
    "answer": "(7, 9)"
  },
  {
    "q": "Find the length of a line segment formed by the points A(1, 2) and B(4, 6).",
    "options": [
      "3",
      "4",
      "5",
      "6"
    ],
    "answer": "5"
  },
  {
    "q": "Simplify $\\left(\\frac{x^{1/2} + x^{-1/2}}{x^{1/2} - x^{-1/2}}\\right)^2$.",
    "options": [
      "$\\frac{(x+1)^2}{(x-1)^2}$",
      "$\\frac{x+1}{x-1}$",
      "$\\frac{x^2+1}{x^2-1}$",
      "$x$"
    ],
    "answer": "$\\frac{(x+1)^2}{(x-1)^2}$"
  },
          {"q": "The value of $\\frac{\\sin 150 - 5 \\cos 300 + 7 \\tan 225}{\\tan 135 + 3 \\sin 210}$ is", "options": ["1", "-1", "2", "-2"], "answer": "-2"},
        {"q": "If $\\log_{10} 2 = 0.3010$ and $\\log_{10} 3 = 0.4771$, the value of $\\log_{10} 12$ is", "options": ["0.7781", "1.0791", "1.1091", "0.9030"], "answer": "1.0791"},
        {"q": "The simplified form of the complex expression $\\frac{3 + 4i}{1 - 2i}$ is", "options": ["-1 + 2i", "1 + 2i", "-1 - 2i", "2 + i"], "answer": "-1 + 2i"},
        {"q": "If the roots of $x^2 - px + q = 0$ are consecutive integers, then $p^2 - 4q$ is equal to", "options": ["1", "2", "3", "4"], "answer": "1"},
        {"q": "The value of $x$ that satisfies $9^{x-1} = 27^{x+2}$ is", "options": ["-8", "8", "-4", "4"], "answer": "-8"},
        {"q": "The expression $\\sqrt{7 + 4\\sqrt{3}}$ is equivalent to", "options": ["2 + \\sqrt{3}", "2 - \\sqrt{3}", "3 + \\sqrt{2}", "4 + \\sqrt{3}"], "answer": "2 + \\sqrt{3}"},
        {"q": "The distance between the parallel lines $3x - 4y + 7 = 0$ and $3x - 4y - 3 = 0$ is", "options": ["1", "2", "3", "4"], "answer": "2"},
        {"q": "The equation of the tangent to the circle $x^2 + y^2 = 25$ at the point $(3, -4)$ is", "options": ["3x - 4y = 25", "3x + 4y = 25", "4x - 3y = 25", "4x + 3y = 25"], "answer": "3x - 4y = 25"},
        {"q": "The coefficient of $x^4$ in the expansion of $(1 + 2x)^6$ is", "options": ["240", "15", "60", "160"], "answer": "240"},
        {"q": "In a Geometric Progression, if the first term is 5 and the common ratio is 2, the sum of the first 6 terms is", "options": ["315", "310", "160", "630"], "answer": "315"},
        {"q": "If $f(x) = \\frac{x-1}{x+1}$, then $f(f(x))$ is equal to", "options": ["x", "1/x", "-1/x", "-x"], "answer": "-1/x"},
        {"q": "In a class of 50 students, 30 study Math, 25 study Physics, and 10 study neither. How many study both?", "options": ["15", "5", "10", "20"], "answer": "15"},
        {"q": "The coordinates of the vertex of the parabola $y = 2x^2 - 8x + 5$ are", "options": ["(2, -3)", "(-2, 3)", "(2, 3)", "(-2, -3)"], "answer": "(2, -3)"},
        {"q": "The value of $\\frac{\\sin 150^\\circ - 5 \\cos 300^\\circ + 7 \\tan 225^\\circ}{\\tan 135^\\circ + 3 \\sin 210^\\circ}$ is", "options": ["1", "-1", "2", "-2"], "answer": "-2"},
        {"q": "If $z = \\frac{1 + i\\sqrt{3}}{1 - i\\sqrt{3}}$, the argument of $z$ in radians is", "options": ["$\\frac{\\pi}{3}$", "$\\frac{2\\pi}{3}$", "$\\pi$", "$\\frac{\\pi}{6}$"], "answer": "$\\frac{2\\pi}{3}$"},
        {"q": "The value of $x$ satisfying $\\log_2(\\log_3 x) = 1$ is", "options": ["3", "6", "9", "8"], "answer": "9"},
        {"q": "If the roots of $ax^2 + bx + c = 0$ are reciprocal to each other, then which condition is true?", "options": ["$a = b$", "$a = c$", "$b = c$", "$a + b + c = 0$"], "answer": "$a = c$"},
        {"q": "Solve for $x$ if $3^{2x+1} - 10(3^x) + 3 = 0$", "options": ["1, -1", "1, 0", "0, -1", "3, 1/3"], "answer": "1, -1"},
        {"q": "Simplify the expression $\\frac{1}{\\sqrt{3} + \\sqrt{2}} + \\frac{1}{\\sqrt{3} - \\sqrt{2}}$", "options": ["$2\\sqrt{3}$", "$2\\sqrt{2}$", "$\\sqrt{6}$", "0"], "answer": "$2\\sqrt{3}$"},
        {"q": "The gradient of the line passing through the point $(1, 2)$ and the midpoint of $(2, 3)$ and $(4, 7)$ is", "options": ["3", "1.5", "2", "1"], "answer": "3"},
        {"q": "The length of the diameter of the circle $x^2 + y^2 - 4x + 6y - 3 = 0$ is", "options": ["4", "8", "16", "2"], "answer": "8"},
        {"q": "If $f(x) = 2x + 1$ and $g(x) = x^2 - 2$, find the composite value $g(f(-2))$", "options": ["7", "11", "9", "-5"], "answer": "7"},
        {"q": "If $A \\subset B$, then the intersection $A \\cap B$ is equal to", "options": ["$A$", "$B$", "$\\emptyset$", "$U$"], "answer": "$A$"},
        {"q": "The coefficient of $x^3$ in the expansion of $(1 - 2x)^5$ is", "options": ["-80", "80", "-40", "40"], "answer": "-80"},
        {"q": "The sum of the first $n$ terms of an AP is $3n^2 + n$. The common difference is", "options": ["3", "6", "2", "4"], "answer": "6"},
        {"q": "The minimum value of the quadratic curve $y = x^2 - 6x + 10$ is", "options": ["1", "3", "10", "0"], "answer": "1"},
        {"q": "The product of $(2 + 5i)$ and its conjugate is", "options": ["29", "21", "29 + 20i", "-21"], "answer": "29"},
        {"q": "The center and radius of the circle $(x+5)^2 + (y-2)^2 = 16$ are", "options": ["(-5, 2), r=4", "(5, -2), r=4", "(-5, 2), r=16", "(5, -2), r=16"], "answer": "(-5, 2), r=4"},
        {"q": "Rationalize the denominator of $\\frac{2}{\\sqrt{5} - \\sqrt{3}}$", "options": ["$\\sqrt{5} + \\sqrt{3}$", "$\\sqrt{5} - \\sqrt{3}$", "$2(\\sqrt{5} + \\sqrt{3})$", "$\\frac{\\sqrt{5} + \\sqrt{3}}{2}$"], "answer": "$\\sqrt{5} + \\sqrt{3}$"},
        {"q": "Simplify $\\frac{2^{n+4} - 2(2^n)}{2(2^{n+3})}$", "options": ["7/8", "1/2", "1/4", "1"], "answer": "7/8"},
        {"q": "If $\\log 2 + \\log(x+3) = \\log(3x+5)$, then $x$ is", "options": ["1", "2", "3", "0"], "answer": "1"},
        {"q": "The sum to infinity of a Geometric Progression with first term 12 and common ratio $1/3$ is", "options": ["18", "24", "36", "12"], "answer": "18"},
        {"q": "The perpendicular distance from the point $(2, 3)$ to the line $3x + 4y + 2 = 0$ is", "options": ["2 units", "4 units", "5 units", "10 units"], "answer": "4 units"},
        {"q": "Simplify $\\sqrt{48} - \\sqrt{12}$", "options": ["$2\\sqrt{3}$", "$4\\sqrt{3}$", "6", "$3\\sqrt{2}$"], "answer": "$2\\sqrt{3}$"},
        {"q": "If $\\log_2 x = 5$, find $x$.", "options": ["32", "10", "25", "64"], "answer": "32"},
        {"q": "The radius of the circle $x^2 + y^2 = 49$ is", "options": ["7", "49", "14", "24.5"], "answer": "7"},
        {"q": "The value of $\\sin^2 30^\\circ + \\cos^2 30^\\circ$ is", "options": ["1", "0.5", "0.25", "2"], "answer": "1"},
        {"q": "Find the sum of the first 5 terms of the AP: 2, 4, 6...", "options": ["30", "20", "25", "40"], "answer": "30"},
        {"q": "The value of $i^2$ is", "options": ["-1", "1", "0", "$i$"], "answer": "-1"},
        {"q": "If $f(x) = 3x - 1$, find $f(2)$.", "options": ["5", "6", "7", "4"], "answer": "5"},
        {"q": "The number of subsets of a set with 3 elements is", "options": ["8", "6", "9", "3"], "answer": "8"},
        {"q": "Evaluate $8^{2/3}$", "options": ["4", "2", "16", "6"], "answer": "4"},
        {"q": "The $y$-intercept of $y = x^2 + 5x + 6$ is", "options": ["6", "5", "0", "-6"], "answer": "6"},
        {"q": "Given that $z_{1} = i$ and $z_{2} = 1 - i$, find $\\frac{z_{1}}{z_{2}}$", "options": ["$\\frac{1}{2}(i - 1)$", "$(i + 1)$", "$\\frac{(1 + i)}{2}$", "$(i - 1)$"], "answer": "$\\frac{1}{2}(i - 1)$"},
        {"q": "In how many ways can three objects be selected out of five distinct objects?", "options": ["15", "10", "60", "120"], "answer": "10"},
        {"q": "If p and q are integers and is represented in the form of $p/q$, then it is a:", "options": ["Whole number", "Rational number", "Natural number", "Even number"], "answer": "Rational number"},
        {"q": "For some integer n, the odd integer is represented in the form of:", "options": ["n", "$n + 1$", "$2n + 1$", "2n"], "answer": "$2n + 1$"},
        {"q": "Find the coefficient of x in the binomial expansion of $(1 - 2x)^{7}$", "options": ["-332", "28", "560", "-56"], "answer": "-56"},
        {"q": "For the principle of mathematical induction to be true, what type of number should 'n' be?", "options": ["Rational Number", "Whole Number", "Natural Number", "Integers"], "answer": "Natural Number"},
        {"q": "Which of the following is a necessary step for proving $1 + 3 + 5 + ... + (2n - 1) = n^{2}$?", "options": ["Verify for $n = k$", "Assume $1 + 3 + ... + k$ is true and prove for $P(k + 1)$", "Prove that $n = 1$ is true", "Prove that $1 + 3 + ... + 2k + 1 = (n + 1)^{2}$"], "answer": "Assume $1 + 3 + ... + k$ is true and prove for $P(k + 1)$"},
        {"q": "Find the equation of the normal to the circle $x^{2} + y^{2} + 3x - 2y = 0$ at the point (3, 2).", "options": ["$2x - 9y + 12 = 0$", "$9x - 2y + 12 = 0$", "$2x - 3y = 6$", "$9x + 2y = 3$"], "answer": "$2x - 9y + 12 = 0$"},
        {"q": "What is the sum of the coefficients in the binomial expansion of $(x - y)^{n}$?", "options": ["n", "1", "0", "-n"], "answer": "0"},
        {"q": "The sum $1^{3} + 2^{3} + ... + n^{3}$ is?", "options": ["$\\frac{n(n + 1)}{2}$", "$(\\frac{n + 1}{2})^{2}$", "$\\frac{n^{2}(n + 1)^{2}}{4}$", "$(\\frac{n(n - 1)}{2})^{2}$"], "answer": "$\\frac{n^{2}(n + 1)^{2}}{4}$"},
        {"q": "In a class of 34 students, 24 are good in English while 15 are good in Mathematics. How many of them are good in both subjects?", "options": ["39", "5", "35", "9"], "answer": "5"},
        {"q": "Simplify $\\frac{9x^{2} + 6x - 3}{9x^{2} - 9}$", "options": ["$\\frac{3x - 1}{3(x - 1)}$", "$\\frac{6x - 1}{3(2x - 1)}$", "$\\frac{2x - 1}{5(x - 1)}$", "$\\frac{2x - 1}{9(3x - 1)}$"], "answer": "$\\frac{3x - 1}{3(x - 1)}$"},
        {"q": "The exact value of $\\cos 35^{\\circ} \\cos 25^{\\circ} - \\sin 35^{\\circ} \\sin 25^{\\circ}$ is:", "options": ["$\\frac{1}{2}$", "$\\sqrt{3}$", "$\\frac{1}{4}$", "$\\frac{\\sqrt{3}}{2}$"], "answer": "$\\frac{1}{2}$"},
        {"q": "Which set is the subset of all given sets?", "options": ["{1,2,3}", "{1}", "{0,1,6,7}", "Ø"], "answer": "Ø"},
        {"q": "A circle whose diameter touches the circumference at the points (-3, 6) and (5, 4) is represented by the equation ...............", "options": ["$x^{2}+y^{2}+3x-2y+2=0$", "$x^{2}+y^{2}-3x+4y+2=0$", "$x^{2}+y^{2}-2x-10y+9=0$", "$4x^{2}+4y^{2}-12x-20y+9=0$"], "answer": "$x^{2}+y^{2}-2x-10y+9=0$"},
        {"q": "The sum of n terms of a certain series is $S_{n}=4^{n}-1$ for all values of n. Find the average of the first three terms of the series.", "options": ["20", "21", "22", "23"], "answer": "21"},
        {"q": "Which of the following identities is not correct?", "options": ["$sin^{2}\\alpha=\\frac{(1-sin~2\\alpha)}{2}$", "$sin^{2}\\alpha=\\frac{(1-cos2\\alpha)}{2}$", "$cos^{2}\\alpha=\\frac{(1+cos2\\alpha)}{2}$", "$sin2\\alpha=2sin\\alpha\\times cos\\alpha$"], "answer": "$sin^{2}\\alpha=\\frac{(1-sin~2\\alpha)}{2}$"},
        {"q": "The triangle formed by the vertices of the points $(-2,8)$, (3,20) and (11,8) is a/an", "options": ["scalene", "right angled", "isosceles", "equilateral"], "answer": "isosceles"},
        {"q": "If $z_{1}=2+i$ and $z_{2}=1+3i$, then $Re(z_{1}z_{2})$ is", "options": ["1", "7i", "i", "-1"], "answer": "-1"},
        {"q": "The sum of the constant coefficients in the expansion of $(1-x)^{10}$ is", "options": ["1024", "900", "0", "$10^{10}$"], "answer": "0"},
        {"q": "If $x^{2}-2ax+a^{2}=0$, find the value of $\\frac{x}{a}$.", "options": ["-1", "1", "3", "2"], "answer": "1"},
        {"q": "If a, b, and c are in G.P. and $a^{x}=b^{y}=c^{z}$, find $\\frac{1}{x}+\\frac{1}{z}$ in terms of y.", "options": ["$\\frac{y}{4}$", "$\\frac{2}{y}$", "$\\frac{y}{2}$", "$\\frac{2}{\\pi}$"], "answer": "$\\frac{2}{y}$"},
        {"q": "Which of the following is incorrect regarding the real number system?", "options": ["Rational numbers can always be expressed by using terminating decimals or repeating decimals.", "Rational numbers can be written as quotient of two integers.", "Rational numbers are any numbers that can be expressed in the form of $\\frac{a}{b}$, where a and b are integers.", "The real number system is not made up of a set of rational and irrational numbers."], "answer": "The real number system is not made up of a set of rational and irrational numbers."},
        {"q": "Find the fifth term of the sequence given that $a_{1}=2$, $a_{2}=7$ and $a_{k+2}=5a_{k+1}-3a_{k}$.", "options": ["535", "536", "537", "538"], "answer": "535"}

    ],

    "chemistry": [
        {"q": "What is the chemical symbol for water?", "options": ["H2O", "CO2", "O2"], "answer": "H2O"},
        {"q": "Which is an alkali metal?", "options": ["Sodium", "Oxygen", "Chlorine"], "answer": "Sodium"},
    ],

    
     
    


    "gst": 
    

        [
  {
    "q": "An __________ summarizes the accurate content and presentation of a document.",
    "options": [
      "Index",
      "Abstract",
      "Electronic source",
      "Advance search"
    ],
    "answer": "Abstract"
  },
  {
    "q": "The 'period' is also written as __________ in punctuation.",
    "options": [
      "Quotation mark",
      "Colon",
      "Comma",
      "Full stop"
    ],
    "answer": "Full stop"
  },
  {
    "q": "When an adjective is placed before a noun, it is said to be in what position?",
    "options": [
      "Superlative",
      "Attributive",
      "Positive",
      "Comparative"
    ],
    "answer": "Attributive"
  },
  {
    "q": "Identify the imperative sentence below:",
    "options": [
      "Do walk quickly",
      "Take the bus home",
      "I don't believe that!",
      "Let's go to France"
    ],
    "answer": "Take the bus home"
  },
  {
    "q": "The number generated when a library book is catalogued is called:",
    "options": [
      "Library number",
      "Book number",
      "Call number",
      "Cataloguing number"
    ],
    "answer": "Call number"
  },
  {
    "q": "Where information is not provided on time for the purpose for which it is required, it becomes __________.",
    "options": [
      "Irrelevant",
      "Relevant",
      "Useful",
      "Relevant & useful"
    ],
    "answer": "Irrelevant"
  },
  {
    "q": "The smallest unit of a word is known as __________.",
    "options": [
      "Phoneme",
      "Phrase",
      "Lexis",
      "Morpheme"
    ],
    "answer": "Morpheme"
  },
  {
    "q": "Which clause pattern is reflected in this sentence: The priest pronounced the couple man and wife.",
    "options": [
      "SVOC",
      "SVOO",
      "SVA",
      "SVC"
    ],
    "answer": "SVOC"
  },
  {
    "q": "Punctuation marks are used for the following except:",
    "options": [
      "To show possessive case in proper and common nouns",
      "To separate subordinate ideas from major ones in a sentence",
      "To indicate stretches of direct speech in a discourse",
      "To indicate a writer's background"
    ],
    "answer": "To indicate a writer's background"
  },
  {
    "q": "The mnemonic __________ serves as a guide to productive study reading.",
    "options": [
      "NEARER",
      "LEARNER",
      "REALER",
      "REARER"
    ],
    "answer": "LEARNER"
  },
  {
    "q": "When searching for any book on Mathematics in the University of Lagos Library, which shelf would you go to?",
    "options": [
      "Shelf NA",
      "Shelf HA",
      "Shelf QA",
      "Shelf QR"
    ],
    "answer": "Shelf QA"
  },
  {
    "q": "Which of the following is NOT true about writing a summary?",
    "options": [
      "Quotations from the text are included",
      "The present tense is used",
      "The major facts are included",
      "Expressions are paraphrased with new words"
    ],
    "answer": "Quotations from the text are included"
  },
  

  {
    "q": "There are __________ sounds altogether in English.",
    "options": [
      "26",
      "24",
      "20",
      "44"
    ],
    "answer": "44"
  },
  {
    "q": "Terminal punctuation includes all except one:",
    "options": [
      "Exclamation mark",
      "Question mark",
      "Full stop",
      "Comma"
    ],
    "answer": "Comma"
  },
  {
    "q": "Study reading does NOT __________.",
    "options": [
      "Increase better study habits",
      "Enhance reading speed",
      "Help students to study smartly and pass well",
      "Boost one's effort towards studying and passing exams"
    ],
    "answer": "Enhance reading speed"
  },
  {
    "q": "A library's entire holdings are kept in a manual database called __________.",
    "options": [
      "Library holdings",
      "Library catalogue",
      "Check list",
      "Book box"
    ],
    "answer": "Library catalogue"
  },
  {
    "q": "Which one of these sentences does NOT contain an interrogative pronoun?",
    "options": [
      "Who are you?",
      "Can you be my friend?",
      "Whom should I tell to follow me?",
      "Whose book is this?"
    ],
    "answer": "Can you be my friend?"
  },
  {
    "q": "Another name for an adjective clause is:",
    "options": [
      "Relative clause",
      "Blackball clause",
      "Restrictive clause",
      "Preemptive clause"
    ],
    "answer": "Relative clause"
  },
  {
    "q": "English stress is __________.",
    "options": [
      "Free",
      "Fixed",
      "Ordered",
      "Mixed"
    ],
    "answer": "Free"
  },
  {
    "q": "The letter <a> is pronounced /i/ in __________.",
    "options": [
      "Pass",
      "Village",
      "Many",
      "Woman"
    ],
    "answer": "Village"
  },
  {
    "q": "The person who provides reference services is called __________.",
    "options": [
      "University Librarian",
      "Reference Librarian",
      "Chief Librarian",
      "Library Officer"
    ],
    "answer": "Reference Librarian"
  },
  {
    "q": "When you retrieve research results that are too broad or unrelated, the way out is to __________.",
    "options": [
      "Change your location",
      "Change your search strategy",
      "Change your topic",
      "Change the author"
    ],
    "answer": "Change your search strategy"
  },
  {
    "q": "Sentences can be grouped into all but one of the following types:",
    "options": [
      "Interlocutory",
      "Declarative",
      "Interrogative",
      "Exclamatory"
    ],
    "answer": "Interlocutory"
  },
  {
    "q": "The ability to recognize when information is needed is called __________.",
    "options": [
      "Information explosion",
      "Information literacy",
      "Information knowledge",
      "Data"
    ],
    "answer": "Information literacy"
  },
  {
    "q": "A thesaurus is a __________.",
    "options": [
      "Simplified dictionary",
      "Pictorial dictionary",
      "Phonetic dictionary",
      "Specialized dictionary"
    ],
    "answer": "Specialized dictionary"
  },
  
  {
    "q": "If you stay in water too long, your fingertips will __________.",
    "options": [
      "Shriveal",
      "Shrivel",
      "Shrivle",
      "Shrivell"
    ],
    "answer": "Shrivel"
  },
  {
    "q": "One of the major benefits of using library databases is __________.",
    "options": [
      "The fast internet speed",
      "The value you get for your money",
      "That they are subscribed to by the library to support students' assignments and research",
      "All of the above"
    ],
    "answer": "That they are subscribed to by the library to support students' assignments and research"
  },
  {
    "q": "__________ is the process of translating written or printed symbols and letters into words and sentences which convey meaning.",
    "options": [
      "Listening",
      "Writing",
      "Speaking",
      "Reading"
    ],
    "answer": "Reading"
  },
  {
    "q": "The __________ criterion for stress prediction takes the internal structure of the word into consideration.",
    "options": [
      "Semantic",
      "Morphological",
      "Syntactic",
      "Phonological"
    ],
    "answer": "Morphological"
  },
  {
    "q": "_________________ is the high, back tense vowel.",
    "options": [
      "/a:/",
      "/i:/",
      "/u:/",
      "/3:/"
    ],
    "answer": "/u:/"
  },
  {
    "q": "A/An _________________ paragraph describes a series of events or a process in some sort of order.",
    "options": [
      "explanation",
      "sequence",
      "evaluation",
      "descriptive"
    ],
    "answer": "sequence"
  },
  {
    "q": "One of these is not a type of subordinate clause.",
    "options": [
      "The Finite Clause",
      "The Verbless Clause",
      "The Non-finite Clause",
      "Infinite Clause"
    ],
    "answer": "Infinite Clause"
  },
  {
    "q": "Fact sources at the University of Lagos Library are housed at the __________.",
    "options": [
      "Reference section",
      "Boulos Library",
      "Automation section",
      "MTN Library"
    ],
    "answer": "Reference section"
  },
  {
    "q": "Zero stress refers to:",
    "options": [
      "primary stress",
      "tertiary stress",
      "secondary stress",
      "unstressed syllables"
    ],
    "answer": "unstressed syllables"
  },
  {
    "q": "Which of the following should not be capitalised?",
    "options": [
      "Gaelic",
      "Chilean",
      "Guesstimates",
      "Guatemalan"
    ],
    "answer": "Guesstimates"
  },
  {
    "q": "The word 'boys' is made up of:",
    "options": [
      "prefix and base word",
      "base word only",
      "base word and suffix",
      "affix and verb"
    ],
    "answer": "base word and suffix"
  },
  {
    "q": "All of these are advantages of using advanced search EXCEPT ___________.",
    "options": [
      "ability to use multiple search fields",
      "ability to reduce number of items retrieved",
      "ability to filter search",
      "ability to retrieve huge amount of information"
    ],
    "answer": "ability to retrieve huge amount of information"
  },
  {
    "q": "The word 'responsibility' is correctly stressed as ____________.",
    "options": [
      "'responsibility",
      "re'sponsibility",
      "responsi'bility",
      "respon'sibility"
    ],
    "answer": "responsi'bility"
  },
  {
    "q": "Questions which require you to refer directly to the text are called ____________.",
    "options": [
      "direct reference questions",
      "evaluation questions",
      "inference questions",
      "supposition questions"
    ],
    "answer": "direct reference questions"
  },
  {
    "q": "______________________ is not a key element to look out for when reading a material.",
    "options": [
      "the conclusion",
      "spelling errors",
      "the introductory section",
      "the author's main point"
    ],
    "answer": "spelling errors"
  },
  {
    "q": "Generally, information sources are divided into the following categories:",
    "options": [
      "Primary only",
      "Tertiary only",
      "Secondary only",
      "Primary & Tertiary"
    ],
    "answer": "Primary & Tertiary"
  },
  {
    "q": "_________________ is not a step in paragraph development.",
    "options": [
      "none of the above",
      "giving examples",
      "choosing a controlling idea",
      "explaining the controlling idea"
    ],
    "answer": "none of the above"
  },
  {
    "q": "_________________ is the informed evaluation of imaginative writing.",
    "options": [
      "coherence",
      "essay writing",
      "blogging",
      "criticism"
    ],
    "answer": "criticism"
  },
  {
    "q": "The expression 'Olu has lived in England before' is an example of what tense?",
    "options": [
      "Simple present",
      "Simple future",
      "Simple past",
      "Simple continuous"
    ],
    "answer": "Simple past"
  },
  {
    "q": "In the expression: 'Tunde and his wife appreciate each other,' the word 'each other' can be described as a __________.",
    "options": [
      "reflexive pronoun",
      "definite pronoun",
      "reciprocal pronoun",
      "relative pronoun"
    ],
    "answer": "reciprocal pronoun"
  },
  {
    "q": "With copyright law, one can use another person's work without permission.",
    "options": [
      "True",
      "Partially True",
      "False",
      "Partially false"
    ],
    "answer": "False"
  },
  {
    "q": "'The man jogs regularly.' Identify the adverb type.",
    "options": [
      "adverb of frequency",
      "adverb of manner",
      "adverb of place",
      "adverb of time"
    ],
    "answer": "adverb of frequency"
  },
  {
    "q": "'Map of Nigeria' and 'Travel guide' are examples of ____________.",
    "options": [
      "Geographical source",
      "Bibliography",
      "Reference source",
      "Biographical source"
    ],
    "answer": "Geographical source"
  },
  {
    "q": "Another name for the argumentative essay is __________ essay.",
    "options": [
      "authoritative",
      "rational",
      "expository",
      "persuasive"
    ],
    "answer": "persuasive"
  },
  {
    "q": "A simple sentence has:",
    "options": [
      "two clauses and no finite verb",
      "one clause and contains only two finite verbs",
      "two clauses and contains only one finite verb",
      "one clause and contains only one finite verb"
    ],
    "answer": "one clause and contains only one finite verb"
  },
  {
    "q": "Reference materials include the following EXCEPT:",
    "options": [
      "Encyclopedia",
      "Journals",
      "Dictionaries",
      "Indexes"
    ],
    "answer": "Journals"
  },
  {
    "q": "Which of these clause types is not a subordinate clause?",
    "options": [
      "adverb clause",
      "adjective clause",
      "prepositional clause",
      "noun clause"
    ],
    "answer": "prepositional clause"
  },
  {
    "q": "The main function of __________ is to separate independent clauses.",
    "options": [
      "comma",
      "exclamation mark",
      "semi-colon",
      "colon"
    ],
    "answer": "semi-colon"
  },
  {
    "q": "Which of the following statements is not correct?",
    "options": [
      "function words are always stressed",
      "noun phrases are stressed on the rightmost constituent",
      "compound nouns are usually stressed on the first constituent",
      "nouns are usually stressed"
    ],
    "answer": "function words are always stressed"
  },
  {
    "q": "Article/journal search can be carried out or done in these sections of the library:",
    "options": [
      "Cataloguing Section",
      "Acquisition Section",
      "Serials and E-library",
      "University Librarian's Office"
    ],
    "answer": "Serials and E-library"
  },
  {
    "q": "The __________ sentence is the most important sentence in a paragraph.",
    "options": [
      "topic",
      "concluding",
      "first",
      "last"
    ],
    "answer": "topic"
  },
  {
    "q": "During lectures, we engage in __________ listening.",
    "options": [
      "total",
      "formal",
      "informal",
      "partial"
    ],
    "answer": "formal"
  },
  {
    "q": "______________ is the use of the pitch of the voice to convey meaning or syntactic information.",
    "options": [
      "rhythm",
      "intonation",
      "stress",
      "phonetics"
    ],
    "answer": "intonation"
  },
  {
    "q": "The 'NOT' operator is used to __________.",
    "options": [
      "include and broaden search",
      "none",
      "exclude and narrow search",
      "connect words"
    ],
    "answer": "exclude and narrow search"
  },
  {
    "q": "The name of an author whose idea is cited in research writing must appear in the __________.",
    "options": [
      "publishers list",
      "publication list",
      "reference list",
      "sources list"
    ],
    "answer": "reference list"
  },
  {
    "q": "University of Lagos Library has __________ library resources.",
    "options": [
      "non-print resources only",
      "print, non-print, and audio-visual resources",
      "print resources only",
      "audio-visual resources only"
    ],
    "answer": "print, non-print, and audio-visual resources"
  },
  {
    "q": "______________ is not a constituent of the syllable.",
    "options": [
      "phoneme",
      "coda",
      "peak",
      "onset"
    ],
    "answer": "phoneme"
  },
  {
    "q": "_____________ allows a user to apply multiple search fields.",
    "options": [
      "Advanced search",
      "Complex search",
      "Quick search",
      "Simple search"
    ],
    "answer": "Advanced search"
  },
  {
    "q": "In interpreting the results of experiments, __________ is/are often explored.",
    "options": [
      "critique",
      "all of the above",
      "rationalisation",
      "empirical methods"
    ],
    "answer": "empirical methods"
  },
  {
    "q": "Enquiries on how to access any of the resources in a library can be made at the __________ Section.",
    "options": [
      "Serials",
      "Akintunde Ojo Building",
      "Readers' Services",
      "Reference"
    ],
    "answer": "Reference"
  },
  {
    "q": "Vowel distinctions do not include:",
    "options": [
      "quadriphthongs",
      "monophthongs",
      "triphthongs",
      "diphthongs"
    ],
    "answer": "quadriphthongs"
  },
  {
    "q": "One of the following is not a component of a good paragraph.",
    "options": [
      "concluding sentence",
      "supporting details",
      "a topic sentence",
      "conflicting details"
    ],
    "answer": "conflicting details"
  },
  {
    "q": "A useful search tool for academic information is ____________.",
    "options": [
      "Opera Mini",
      "Google",
      "Web crawler",
      "Google Scholar"
    ],
    "answer": "Google Scholar"
  },
  {
    "q": "The Boolean operator 'OR' is used in a search to ____________.",
    "options": [
      "differentiate words",
      "all",
      "exclude words",
      "connect synonyms"
    ],
    "answer": "connect synonyms"
  },
  {
    "q": "Boolean operators are:",
    "options": [
      "AND, OR, NOT",
      "DVD players",
      "computer databases",
      "AND, BUT, OR"
    ],
    "answer": "AND, OR, NOT"
  },
  {
    "q": "When you paraphrase a quote, ____________.",
    "options": [
      "you use the exact words",
      "you reuse it in another language",
      "you use your own words",
      "you quote verbatim"
    ],
    "answer": "you use your own words"
  },
  {
    "q": "The abbreviation NEC in note-taking means ____________.",
    "options": [
      "Non-Essential Creatures",
      "National Executive Council",
      "National Electoral Commission",
      "Necessary"
    ],
    "answer": "Necessary"
  },
  {
    "q": "A dictionary aids vocabulary development by ____________.",
    "options": [
      "all of the above",
      "indicating the ways the words are pronounced",
      "suggesting meanings of words",
      "indicating the context of usage and spelling"
    ],
    "answer": "all of the above"
  },
  {
    "q": "Speech is related to the respiratory system because it involves the ____________.",
    "options": [
      "nose",
      "larynx",
      "lips",
      "lungs"
    ],
    "answer": "lungs"
  },
  {
    "q": "As a prefix, ANTI- means ____________.",
    "options": [
      "similar",
      "congruent",
      "against",
      "dissimilar"
    ],
    "answer": "against"
  },
  {
    "q": "Recalling stored information is enhanced by the following EXCEPT ____________.",
    "options": [
      "repetition",
      "reproduction",
      "review",
      "recitation"
    ],
    "answer": "reproduction"
  },
  {
    "q": "Referencing is composed of two parts, namely __________.",
    "options": [
      "Out-text referencing and bibliographies",
      "On-text referencing and guide list",
      "In-text referencing and reference list",
      "Off-text referencing and referral list"
    ],
    "answer": "In-text referencing and reference list"
  },
  {
    "q": "The airstream that is used for the production of most English sounds is the __________ airstream.",
    "options": [
      "Glottalic",
      "Velaric",
      "Pulmonic",
      "Laryngeal"
    ],
    "answer": "Pulmonic"
  },
  {
    "q": "Biographical sources are reference materials that provide individual information such as __________.",
    "options": [
      "Date of birth",
      "All of the above",
      "Place of birth",
      "Career achievements"
    ],
    "answer": "All of the above"
  },
  {
    "q": "The syllable in a word which has a __________ vowel quality usually attracts stress.",
    "options": [
      "Round",
      "High",
      "Strong",
      "Close"
    ],
    "answer": "Strong"
  },
  {
    "q": "Not waiting for the lecture to end before drawing your conclusion on the content suggests __________.",
    "options": [
      "Distraction",
      "Mental challenge",
      "Emotional attachment",
      "Hasty generalisation"
    ],
    "answer": "Hasty generalisation"
  },
  {
    "q": "Which of the following is a compound noun?",
    "options": [
      "An English teacher",
      "Greenhouse",
      "Black bird",
      "White House"
    ],
    "answer": "Greenhouse"
  },
  {
    "q": "Grammar is the study of __________.",
    "options": [
      "Sentence structure",
      "Words and sentences",
      "Phrase structure",
      "Sentence combination"
    ],
    "answer": "Words and sentences"
  },
  {
    "q": "One of the following skills is not necessary in note-taking.",
    "options": [
      "Summary",
      "Sentence reduction",
      "Paraphrasing",
      "Sound articulation"
    ],
    "answer": "Sound articulation"
  },
  {
    "q": "In English, __________ is one of the best ways to acquire new words.",
    "options": [
      "Cultural exchange",
      "Reading widely",
      "Vocalization",
      "Watching movies"
    ],
    "answer": "Reading widely"
  },
  {
    "q": "The base word in 'Educational' is __________.",
    "options": [
      "Educate",
      "Duct",
      "Nal",
      "Ed"
    ],
    "answer": "Educate"
  },
  {
    "q": "APA recommends that a book without an author should be cited in the text using __________.",
    "options": [
      "The first few words of the title, year of publication, and page number",
      "The title",
      "All of the above",
      "Year of publication"
    ],
    "answer": "The first few words of the title, year of publication, and page number"
  },
  {
    "q": "In scanning, the __________ can be very important.",
    "options": [
      "Foreword",
      "Preface",
      "Topic sentences",
      "Index"
    ],
    "answer": "Index"
  },
  {
    "q": "Criteria to evaluate credibility of information resources are: currency, authority, __________ and __________.",
    "options": [
      "Strategy and accuracy",
      "Relevancy and intelligence",
      "None",
      "Relevancy and accuracy"
    ],
    "answer": "Relevancy and accuracy"
  },
  {
    "q": "All are eligible for copyright according to the World Intellectual Property Organization, EXCEPT __________.",
    "options": [
      "Painting",
      "Music",
      "Books",
      "Complimentary cards"
    ],
    "answer": "Complimentary cards"
  },
  {
    "q": "The punishment for violating copyright law is __________.",
    "options": [
      "Kill the offender",
      "Prosecute the offender under the law",
      "All of the above",
      "Jail the offender"
    ],
    "answer": "Prosecute the offender under the law"
  },
  {
    "q": "Which clause pattern is reflected in this sentence: The tribunal conducted the hearing behind closed doors.",
    "options": [
      "SVOC",
      "SV",
      "SVOA",
      "SVO"
    ],
    "answer": "SVOA"
  },
  {
    "q": "Which of the following is NOT true of paragraphs?",
    "options": [
      "The argument in a paragraph addresses only an aspect of the topic",
      "They are of varying lengths",
      "Every paragraph begins with a topic sentence",
      "A paragraph is hardly ever longer than the entire essay"
    ],
    "answer": "Every paragraph begins with a topic sentence"
  },
  {
    "q": "The __________ is the major point which an essay seeks to prove.",
    "options": [
      "Thesis",
      "Subject matter",
      "Synopsis",
      "Theme"
    ],
    "answer": "Thesis"
  },
  {
    "q": "__________ combines the manner of articulation of stops and fricatives.",
    "options": [
      "Vowels",
      "Nasals",
      "Glides",
      "Affricates"
    ],
    "answer": "Affricates"
  },
  {
    "q": "__________ is done to reduce the number of items retrieved in advanced search.",
    "options": [
      "Filtering",
      "Exercises",
      "Simple search",
      "Research"
    ],
    "answer": "Filtering"
  },
  {
    "q": "One of the following is a feature shared by both paragraphs and essays:",
    "options": [
      "Transition and cohesion",
      "Unity and self-sufficiency",
      "Cohesion and transparency",
      "Unity and coherence"
    ],
    "answer": "Unity and coherence"
  },
  {
    "q": "Which of the following sentences does NOT have a singular compound subject?",
    "options": [
      "Waiter, is the rice and beans ready?",
      "The MD and Chief Executive Officer of the company was introduced",
      "The manager and all his staff are here.",
      "Hot lemonade and honey is good for a cold."
    ],
    "answer": "The manager and all his staff are here."
  },
  {
    "q": "Electronic journals, electronic images, library software, CD-ROMs are __________.",
    "options": [
      "Print resources",
      "Audio-visual resources",
      "Print and non-print",
      "Non-print resources"
    ],
    "answer": "Non-print resources"
  },
  {
    "q": "One of the reasons for citing published work is __________.",
    "options": [
      "If the author is a lecturer",
      "To acknowledge people's works and ideas",
      "If the person has written many books",
      "If the book is interesting"
    ],
    "answer": "To acknowledge people's works and ideas"
  },
  {
    "q": "One of these is not a type of pronoun.",
    "options": [
      "Refractive pronouns",
      "Possessive pronouns",
      "Interrogative pronouns",
      "Relative pronouns"
    ],
    "answer": "Refractive pronouns"
  },
  {
    "q": "Multimedia information pertains to the use of diversified media of communication such as __________.",
    "options": [
      "Numbers",
      "Text",
      "Graphs",
      "Audio-visual"
    ],
    "answer": "Audio-visual"
  },
  {
    "q": "Mr. Dokunboh thanked the lady. 'The lady' is the __________.",
    "options": [
      "Subject of the verb",
      "Object complement",
      "Indirect object of the verb",
      "Direct object of the verb"
    ],
    "answer": "Direct object of the verb"
  },
  {
    "q": "The URL of a website accredited to a post-secondary institution usually ends with __________.",
    "options": [
      ".gov",
      ".org",
      ".com",
      ".edu"
    ],
    "answer": ".edu"
  },
  {
    "q": "A word usually has __________ primarily stressed syllable(s).",
    "options": [
      "1",
      "3",
      "4",
      "2"
    ],
    "answer": "1"
  },
  {
    "q": "The word 'challenge' when used as a noun or a verb is respectively stressed as __________.",
    "options": [
      "chalLENGE / CHALlenge",
      "CHALlenge / chalLENGE",
      "CHALLENGE / challenge",
      "CHALlenge / CHALlenge"
    ],
    "answer": "CHALlenge / CHALlenge"
  },
  {
    "q": "The most commonly used citation style in Social Sciences is __________.",
    "options": [
      "Harvard",
      "Chicago",
      "MLA",
      "APA"
    ],
    "answer": "APA"
  },
  {
    "q": "Biographical sources are categorized into __________.",
    "options": [
      "Local and local",
      "Universal and current",
      "A & B",
      "National and local"
    ],
    "answer": "Universal and current"
  },
  {
    "q": "In relation to the tools used by examiners to test candidates' understanding, the following question types can be identified except __________.",
    "options": [
      "Inference question",
      "Evaluation question",
      "Supposition question",
      "Affirmation question"
    ],
    "answer": "Affirmation question"
  },
  {
    "q": "Words can be in any of the following forms except:",
    "options": [
      "Simple",
      "Compound-complex",
      "Compound",
      "Complex"
    ],
    "answer": "Compound-complex"
  },
  {
    "q": "Grammar is categorized into two major sections, namely __________.",
    "options": [
      "Syntax and phonetics",
      "Lexis and morphology",
      "Syntax and semantics",
      "Morphology and syntax"
    ],
    "answer": "Morphology and syntax"
  },
  {
    "q": "The element which makes a paragraph easily understandable to the reader is __________.",
    "options": [
      "Unity",
      "Coherence",
      "Development",
      "Completeness"
    ],
    "answer": "Coherence"
  },
  {
    "q": "A paragraph is complete when it has __________.",
    "options": [
      "A topic sentence and supporting details",
      "An initial capital letter and a final full stop",
      "None of the above",
      "An argument"
    ],
    "answer": "A topic sentence and supporting details"
  },
  {
    "q": "Yearbooks are also known as __________.",
    "options": [
      "Dictionary",
      "Directory",
      "Handbook",
      "Annual"
    ],
    "answer": "Annual"
  },
  {
    "q": "In essay writing, the acronym COEM means __________.",
    "options": [
      "Content, Organisation, Expression, Mechanics",
      "Content, Organisation, Entertainment, Mechanics",
      "Comment, Organisation, Expression, Mechanics",
      "Content, Orientation, Expression, Mechanics"
    ],
    "answer": "Content, Organisation, Expression, Mechanics"
  },
  {
    "q": "Copyrighted works are protected by __________.",
    "options": [
      "Bookseller",
      "The author",
      "Law",
      "Publisher"
    ],
    "answer": "Law"
  },
  {
    "q": "The mechanism for accessing information in the library is through __________.",
    "options": [
      "Book catalogue",
      "Google and search engines",
      "Card catalogue and OPAC",
      "Mobile phone and accessories"
    ],
    "answer": "Card catalogue and OPAC"
  },
  {
    "q": "Which of the following is NOT a quality of a good topic sentence?",
    "options": [
      "Expanded",
      "Emphatic",
      "Concise",
      "Restricted"
    ],
    "answer": "Expanded"
  },
  {
    "q": "Free morphemes are sub-categorized into __________.",
    "options": [
      "Grammatical and functional",
      "Functional and descriptive",
      "Descriptive and functional",
      "Lexical and functional"
    ],
    "answer": "Lexical and functional"
  },
  {
    "q": "Skimming can be classified under __________.",
    "options": [
      "Reading with intent",
      "None of the above",
      "Review after reading",
      "Preview before reading"
    ],
    "answer": "Preview before reading"
  },
  {
    "q": "Declarative sentences end with a/an __________.",
    "options": [
      "Period",
      "Exclamation point",
      "Comma",
      "Question mark"
    ],
    "answer": "Period"
  },
  {
    "q": "Prefixes and suffixes are generally known as __________.",
    "options": [
      "Stem",
      "Affixation",
      "Affixes",
      "Root"
    ],
    "answer": "Affixes"
  },
  {
    "q": "Students are advised to maintain __________ contact with their lecturers during classes.",
    "options": [
      "Close",
      "Virtual",
      "Full",
      "Eye"
    ],
    "answer": "Eye"
  },
  {
    "q": "A/an __________ is a condensed version of an original work.",
    "options": [
      "Summary",
      "Blurb",
      "Abstract",
      "Preface"
    ],
    "answer": "Summary"
  },
  {
    "q": "UNILAG students have remote access to UNILAG Library online resources via __________.",
    "options": [
      "The telephone directory",
      "UNILAG Library website",
      "Hall of residence",
      "Matric number"
    ],
    "answer": "UNILAG Library website"
  },
  {
    "q": "The __________ is used before a list of items.",
    "options": [
      "Question mark",
      "Semicolon",
      "Period",
      "Colon"
    ],
    "answer": "Colon"
  },
  {
    "q": "One of these is not a minor sentence.",
    "options": [
      "No vacancy",
      "Gatekeeper wanted",
      "No fuel",
      "God bless you"
    ],
    "answer": "God bless you"
  },
  {
    "q": "When using the APA referencing style, the reference list should be arranged in __________ order.",
    "options": [
      "Numerical",
      "Citation",
      "Chronological",
      "Alphabetical"
    ],
    "answer": "Alphabetical"
  },
  {
    "q": "The research and bibliographic section of the library houses __________.",
    "options": [
      "PhD thesis",
      "Law books",
      "Old and current newspapers",
      "A & C"
    ],
    "answer": "PhD thesis"
  },
  {
    "q": "Symbols used in phonetic transcription are adapted from __________.",
    "options": [
      "MLA",
      "APA",
      "PLA",
      "IPA"
    ],
    "answer": "IPA"
  },
  {
    "q": "Students can search the manual library catalogue for information materials using __________.",
    "options": [
      "None",
      "Author/series & subject",
      "Author/title & keyword",
      "Author/title & subject"
    ],
    "answer": "Author/title & subject"
  },
  {
    "q": "My mother cooks very well. 'Very well' is an __________.",
    "options": [
      "Adverb of degree",
      "Adverb of time",
      "Adverb of manner",
      "Adverb of place"
    ],
    "answer": "Adverb of manner"
  },
  {
    "q": "Secondary source is more reliable than primary source.",
    "options": [
      "True",
      "I don't know",
      "Very true",
      "False"
    ],
    "answer": "False"
  },
  {
    "q": "In-text citation appears in the manuscript.",
    "options": [
      "Partially false",
      "Partially true",
      "False",
      "True"
    ],
    "answer": "True"
  },
  {
    "q": "Subject searching allows one to __________.",
    "options": [
      "Browse for items by phrase heading",
      "Browse from Library OPAC",
      "Browse for items by subject",
      "Browse for items by clause heading"
    ],
    "answer": "Browse for items by subject"
  },
  {
    "q": "Citation is a skill that must be learnt __________.",
    "options": [
      "For library usage",
      "For information retrieval",
      "For chatting online",
      "For academic purposes"
    ],
    "answer": "For academic purposes"
  },
  {
    "q": "The label 'bilabial glide' refers to __________.",
    "options": [
      "/w/",
      "/m/",
      "/b/",
      "/p/"
    ],
    "answer": "/w/"
  },
  {
    "q": "To achieve depth in the treatment of a topic, the writer is advised to __________.",
    "options": [
      "Expand the subject",
      "Manage transition",
      "Punctuate words appropriately",
      "Limit/narrow the subject"
    ],
    "answer": "Limit/narrow the subject"
  },
  {
    "q": "__________ are the meaningful items occurring in a sentence or cluster of sentences, expressed in symbols rather than in words.",
    "options": [
      "Mechanics",
      "Contents",
      "Paragraphs",
      "Expressions"
    ],
    "answer": "Mechanics"
  },
  {
    "q": "Which clause pattern is reflected in this sentence: Jesus wept.",
    "options": [
      "SVO",
      "SVC",
      "SV",
      "SVA"
    ],
    "answer": "SV"
  },
  {
    "q": "One of the following is NOT essential to reading:",
    "options": [
      "Written signs",
      "The eyes",
      "The articulatory system",
      "Printed signs"
    ],
    "answer": "The articulatory system"
  },
  {
    "q": "__________ words involve two or more independent words.",
    "options": [
      "Compound-complex",
      "Compound",
      "Simple",
      "Complex"
    ],
    "answer": "Compound"
  },
  {
    "q": "Which of the following are irregular nouns?",
    "options": [
      "Leaf–leaves, wife–wives, half–halves",
      "Man–men, woman–women, louse–lice",
      "Foot–feet, goose–geese, tooth–teeth",
      "All of the above"
    ],
    "answer": "All of the above"
  },
  {
    "q": "Features which apply to units higher than the segments are known as __________.",
    "options": [
      "Phonologicals",
      "Hierarchicals",
      "Segmentals",
      "Suprasegmentals"
    ],
    "answer": "Suprasegmentals"
  },
  {
    "q": "Reserved collections in University of Lagos Library are run on __________ access system.",
    "options": [
      "Closed",
      "Restricted",
      "Open",
      "Reserve"
    ],
    "answer": "Closed"
  },
  {
    "q": "The words facsimile, prep, gents, zoo, and ad are examples of which word-formation process?",
    "options": [
      "Acronym",
      "Clipping",
      "Conversion",
      "Blend"
    ],
    "answer": "Clipping"
  },
  {
    "q": "Which of the following phrases contains an indefinite article?",
    "options": [
      "My friend",
      "That house",
      "The Golden Globe Awards",
      "A big fat hen"
    ],
    "answer": "A big fat hen"
  },
  {
    "q": "A/an __________ is a summary of a plot.",
    "options": [
      "Episode",
      "Prologue",
      "Storyline",
      "Synopsis"
    ],
    "answer": "Synopsis"
  },
  {
    "q": "The goal of an argumentative essay is to __________.",
    "options": [
      "Convince the readers",
      "Sell an idea",
      "Persuade the audience",
      "All of the above"
    ],
    "answer": "All of the above"
  },
  {
    "q": "__________ is consulted mostly by speech makers and writers.",
    "options": [
      "Book of Quotations",
      "Manual",
      "Biographical book",
      "Book of reference"
    ],
    "answer": "Book of Quotations"
  },
  {
    "q": "The __________ in a paragraph states the main idea in that paragraph and works as its summary.",
    "options": [
      "Topic sentence",
      "Sentence",
      "Punctuation",
      "Conclusion"
    ],
    "answer": "Topic sentence"
  },
  {
    "q": "A research exercise must be __________ driven.",
    "options": [
      "Subject/topic",
      "Lesson plan",
      "Subject plan",
      "Strategy"
    ],
    "answer": "Strategy"
  },
  {
    "q": "Listening can be categorised into __________ and __________.",
    "options": [
      "Good and bad",
      "Past and present",
      "Total and partial",
      "Formal and informal"
    ],
    "answer": "Total and partial"
  },
  {
    "q": "One of the following is NOT true:",
    "options": [
      "A paragraph contains coherent argument",
      "A paragraph can begin with a transition sentence",
      "A paragraph is a unified unit",
      "A paragraph must begin with a topic sentence"
    ],
    "answer": "A paragraph must begin with a topic sentence"
  },
  {
    "q": "The __________ is the only compulsory element in a syllable.",
    "options": [
      "Vowel",
      "Noun",
      "Verb",
      "Consonant"
    ],
    "answer": "Vowel"
  },
  {
    "q": "Which one of the following is a simple sentence?",
    "options": [
      "No smoking.",
      "The boy killed the snake.",
      "The teacher asked a difficult question and no student could answer it.",
      "Ngozi was at the scene, but she didn't witness the accident."
    ],
    "answer": "The boy killed the snake."
  },
  {
    "q": "To avoid plagiarism, all used works must be __________.",
    "options": [
      "Cited",
      "Typed",
      "Noted",
      "Grouped"
    ],
    "answer": "Cited"
  },
  {
    "q": "__________ is used to introduce a list.",
    "options": [
      "Semicolon",
      "Comma",
      "Full stop",
      "Colon"
    ],
    "answer": "Colon"
  },
  {
    "q": "Africana materials are not loanable and users are not permitted to take them out of Gandhi Library.",
    "options": [
      "False",
      "Partially true",
      "Partially false",
      "True"
    ],
    "answer": "True"
  },
  {
    "q": "Advanced search allows you to limit your searches by __________.",
    "options": [
      "Size of book",
      "Year of publication",
      "Volume of book",
      "Number of pages"
    ],
    "answer": "Year of publication"
  },
  {
    "q": "Publications conveying recent original research and observation are known as __________.",
    "options": [
      "Translations",
      "Journals",
      "Tables",
      "Textbooks"
    ],
    "answer": "Journals"
  },
  {
    "q": "A group of words that behave like a single word with a single meaning is known as __________.",
    "options": [
      "Composition",
      "Continuation",
      "Collocation",
      "Connotation"
    ],
    "answer": "Collocation"
  },
  {
    "q": "Ranking of articles retrieved from databases is by __________.",
    "options": [
      "Date and relevance",
      "The number of records",
      "All of the above",
      "Number of times the search was conducted"
    ],
    "answer": "Date and relevance"
  },
  {
    "q": "The reading speed adopted depends on all the following except __________.",
    "options": [
      "The nature of the reading material",
      "The purpose of the reading",
      "The author's prescription",
      "The reader"
    ],
    "answer": "The author's prescription"
  },
  {
    "q": "Bibliography refers to __________.",
    "options": [
      "All of the above",
      "List of books, magazines, articles, etc. about a particular subject",
      "A list of the written sources of information on a subject",
      "A list of books and articles that have been used by someone when writing a subject"
    ],
    "answer": "All of the above"
  },
  {
    "q": "In the sentence 'We bought John a guitar,' the phrase 'a guitar' functions as __________.",
    "options": [
      "Direct object",
      "Subject complement",
      "Indirect object",
      "Object complement"
    ],
    "answer": "Direct object"
  },
  {
    "q": "The meaning ascribed to a word is __________.",
    "options": [
      "Static",
      "Permanent",
      "Diffused",
      "Dynamic"
    ],
    "answer": "Dynamic"
  },
  {
    "q": "The thesis statement is to an essay what the __________ is to a paragraph.",
    "options": [
      "Topic sentence",
      "Supporting details",
      "Introduction",
      "Conclusion"
    ],
    "answer": "Topic sentence"
  },
  {
    "q": "The number generated when a library material is catalogued is called __________.",
    "options": [
      "Library number",
      "Cataloguing number",
      "Call number",
      "Book number"
    ],
    "answer": "Call number"
  },
  {
    "q": "To be elected __________, candidates must have a solid background in law enforcement.",
    "options": [
      "Sheriff",
      "Sherrif",
      "Sherriff",
      "Sherif"
    ],
    "answer": "Sheriff"
  },
  {
    "q": "Dictionaries are used as quick __________ sources in the library.",
    "options": [
      "Publication",
      "Reference",
      "Serial",
      "Manual"
    ],
    "answer": "Reference"
  },
  {
    "q": "Books on Sociology in the University of Lagos Library can be found in __________.",
    "options": [
      "Shelf TA",
      "Shelf HM",
      "Shelf HC",
      "Shelf NA"
    ],
    "answer": "Shelf HM"
  },
  {
    "q": "Another name for the soft palate is the __________.",
    "options": [
      "Alveolar ridge",
      "Palatal",
      "Pharynx",
      "Velum"
    ],
    "answer": "Velum"
  },
  {
    "q": "A complex sentence has __________.",
    "options": [
      "One independent clause and one or more dependent clauses",
      "Two independent clauses and one dependent clause",
      "Two independent clauses and one or more dependent clauses",
      "One independent clause and one dependent clause"
    ],
    "answer": "One independent clause and one or more dependent clauses"
  },
  {
    "q": "When there are too few sources retrieved for a search, one can __________.",
    "options": [
      "Use the AND Boolean operator",
      "None of the above",
      "Combine synonymous terms with the OR Boolean operator",
      "Use the NOT Boolean operator"
    ],
    "answer": "Combine synonymous terms with the OR Boolean operator"
  },
  {
    "q": "Radio, tape recorder, gramophone, and audio cassette player are examples of __________.",
    "options": [
      "Audio materials",
      "Electronic materials",
      "Visual materials",
      "Audio-visual materials"
    ],
    "answer": "Audio-visual materials"
  },
  {
    "q": "__________ is not a referencing style.",
    "options": [
      "MLA (Modern Language Association) style",
      "APA (American Psychological Association) style",
      "Toronto Reference Style",
      "Harvard reference style"
    ],
    "answer": "Toronto Reference Style"
  },
  {
    "q": "Transitions can occur __________.",
    "options": [
      "Only within a paragraph",
      "Only between paragraphs",
      "Either between or within paragraphs",
      "None of the above"
    ],
    "answer": "Either between or within paragraphs"
  },
  {
    "q": "Clear thinking, accurate data, reliable authority, and clear conclusion are applicable to __________ essay.",
    "options": [
      "Descriptive",
      "Analytical",
      "Narrative",
      "Persuasive"
    ],
    "answer": "Analytical"
  },
  {
    "q": "The use of keywords to perform quick information search is known as __________.",
    "options": [
      "Simple search",
      "Meta search",
      "Advanced search",
      "Complex search"
    ],
    "answer": "Simple search"
  },
  {
    "q": "One of the following does not describe a noun:",
    "options": [
      "Can be singular or plural",
      "Has a possessive form",
      "Can be in past or present tense",
      "Can be proper or common"
    ],
    "answer": "Can be in past or present tense"
  },
  {
    "q": "Types of libraries include all of these EXCEPT __________.",
    "options": [
      "Court",
      "Special",
      "Public",
      "Academic"
    ],
    "answer": "Court"
  },
  {
    "q": "Review, as a step in study reading, is synonymous with __________.",
    "options": [
      "Preview",
      "Revision",
      "Scanning",
      "Summary"
    ],
    "answer": "Revision"
  },
  {
    "q": "Internal citation appears in the body of a manuscript.",
    "options": [
      "False",
      "Partially false",
      "Partially true",
      "True"
    ],
    "answer": "True"
  },
  {
    "q": "What is a thesaurus?",
    "options": [
      "Synonymous terms",
      "All of the above",
      "Collection of selected terminology",
      "List of words"
    ],
    "answer": "Synonymous terms"
  },
  {
    "q": "Identify the incorrectly spelled word below:",
    "options": [
      "Souvenier",
      "Vagrant",
      "Resinous",
      "Chauffeur"
    ],
    "answer": "Souvenier"
  },
  {
    "q": "The process of word formation where old words are given new meanings is called __________.",
    "options": [
      "Blending",
      "Neologism",
      "Coining",
      "Mixing"
    ],
    "answer": "Neologism"
  },
  {
    "q": "We need to troubleshoot a paragraph in all the following cases except __________.",
    "options": [
      "When it has issues with transition within the paragraph",
      "When there is a problem with its topic sentence",
      "When it is too long or too short",
      "When it has multiple controlling ideas"
    ],
    "answer": "When it has issues with transition within the paragraph"
  },
  {
    "q": "Information can be in the form of __________.",
    "options": [
      "All",
      "Texts",
      "Numbers",
      "Graphs & charts"
    ],
    "answer": "All"
  },
  {
    "q": "The words tall, taller, tallest are examples of what kind of adjective?",
    "options": [
      "Concrete and abstract",
      "Comparative",
      "Active",
      "Gradeable and non-gradeable"
    ],
    "answer": "Gradeable and non-gradeable"
  },
  {
    "q": "Fair use allows the usage of copyrighted works for __________.",
    "options": [
      "Prosecution purposes",
      "Academic purposes",
      "Publishing purposes",
      "Business purposes"
    ],
    "answer": "Academic purposes"
  },
  {
    "q": "In speech production, __________ of the human body is involved.",
    "options": [
      "A quarter",
      "Three quarters",
      "The whole",
      "Half"
    ],
    "answer": "Half"
  },
  {
    "q": "Functional morphemes in English are otherwise known as __________.",
    "options": [
      "Open classed items",
      "Closed classed items",
      "Adjectives",
      "Modifiers"
    ],
    "answer": "Closed classed items"
  },
  {
    "q": "Prepositions begin phrases that end with __________.",
    "options": [
      "Either a noun or pronoun",
      "Verb or adverb",
      "Conjunction or adjunct",
      "Adjective or pronoun"
    ],
    "answer": "Either a noun or pronoun"
  },
  {
    "q": "Notable reference collection includes all of these EXCEPT __________.",
    "options": [
      "Fact sources",
      "Books",
      "Encyclopaedia",
      "Dictionaries"
    ],
    "answer": "Books"
  },
  {
    "q": "A quote is used in research write-up to __________.",
    "options": [
      "Support an argument",
      "Convince your supervisor",
      "Show off your writing skills",
      "Use vocabulary"
    ],
    "answer": "Support an argument"
  },
  {
    "q": "Post-lecture activities include all the following except __________.",
    "options": [
      "Revision",
      "Disposal",
      "Review",
      "Summary"
    ],
    "answer": "Disposal"
  },
  {
    "q": "Which of these sentences has a plural compound subject?",
    "options": [
      "Hot lemonade and honey is good for a cold.",
      "The man and his wife were present.",
      "The MD and Chief Executive Officer of the company was introduced.",
      "Waiter, is the rice and beans ready?"
    ],
    "answer": "The man and his wife were present."
  },
  {
    "q": "Which clause pattern is reflected in this sentence: 'The plane took off at noon.'",
    "options": [
      "SVOO",
      "SV",
      "SVOA",
      "SVA"
    ],
    "answer": "SVA"
  },
  {
    "q": "3R stands for __________.",
    "options": [
      "Read, Recall, Review",
      "Read, Replay, Rehearse",
      "Read, Roll, Repeat",
      "Read, Recite, Repeat"
    ],
    "answer": "Read, Recall, Review"
  },
  {
    "q": "Manual is a type of reference material that __________.",
    "options": [
      "None",
      "Provides instructions on how to go to places",
      "Provides instructions on how to do things",
      "Provides information on where to find books in the library"
    ],
    "answer": "Provides instructions on how to do things"
  },
  {
    "q": "Reading for the purpose of gathering information that will translate to knowledge is also known as __________.",
    "options": [
      "Scanning",
      "Study reading",
      "Skimming",
      "Exploring"
    ],
    "answer": "Study reading"
  },
  {
    "q": "The three dots used to indicate that some items have been left out in a sentence are known as __________.",
    "options": [
      "Ellipsis",
      "Hyphen",
      "Quotation marks",
      "Dashes"
    ],
    "answer": "Ellipsis"
  },
  {
    "q": "One of the following conditions does not affect listening:",
    "options": [
      "The physical",
      "The physiological",
      "The psychological",
      "The spiritual"
    ],
    "answer": "The spiritual"
  },
  {
    "q": "Employing the use of various search engines in an electronic search is referred to as __________.",
    "options": [
      "Meta search",
      "Upper search",
      "Lower search",
      "Simple search"
    ],
    "answer": "Meta search"
  },
  {
    "q": "The words few, many, little, some, several are known as __________.",
    "options": [
      "Articles",
      "Zero article",
      "Quantifiers",
      "Numerals"
    ],
    "answer": "Quantifiers"
  },
  {
    "q": "Grammar is the study of _______.",
    "options": [
      "Phrase structure",
      "Sentence structure",
      "Words and sentences",
      "Sentence combination"
    ],
    "answer": "Sentence structure"
  },
  {
    "q": "One of the following is not involved in vowel articulation:",
    "options": [
      "Length",
      "Tongue movement",
      "Lip shaping",
      "Contact"
    ],
    "answer": "Contact"
  },
  {
    "q": "When our eyes make a backward movement during reading, it is known as:",
    "options": [
      "Regression",
      "Forwarding",
      "Backwarding",
      "Clearing"
    ],
    "answer": "Regression"
  },
  {
    "q": "The ________ tune is used in declarative sentences.",
    "options": [
      "Fall-rise",
      "Rise-fall",
      "Falling",
      "Rising"
    ],
    "answer": "Falling"
  },
  {
    "q": "The study of the arrangement of constituents within a sentence is called:",
    "options": [
      "Graphology",
      "Syntax",
      "Grammar",
      "Morphology"
    ],
    "answer": "Syntax"
  },
  {
    "q": "The prominence of one syllable over other syllables in a word is a function of:",
    "options": [
      "Pitch",
      "Intensity",
      "Length",
      "Stress"
    ],
    "answer": "Stress"
  },
  {
    "q": "There are how many basic clause patterns in the English simple sentence?",
    "options": [
      "7",
      "6",
      "8",
      "4"
    ],
    "answer": "7"
  },
  {
    "q": "__________ is not a type of abstract.",
    "options": [
      "Evaluative abstracts",
      "Review abstract",
      "Informative abstract",
      "Indicative abstract"
    ],
    "answer": "Review abstract"
  },
  {
    "q": "The following are search techniques EXCEPT:",
    "options": [
      "Truncation",
      "Filtering",
      "Boolean",
      "Wild card"
    ],
    "answer": "Filtering"
  },
  {
    "q": "One of the following is NOT a way of enhancing coherence.",
    "options": [
      "Avoiding the use of pronouns",
      "Using transition words",
      "Repeating keywords",
      "Using synonyms"
    ],
    "answer": "Avoiding the use of pronouns"
  },
  {
    "q": "Reference materials contain facts and rarely contain opinions.",
    "options": [
      "True",
      "Partially true",
      "Partially false",
      "False"
    ],
    "answer": "True"
  },
  {
    "q": "The movement of the eyes in the process of reading can be described as:",
    "options": [
      "Glottalic",
      "Saccadic",
      "Pulmonic",
      "Velaric"
    ],
    "answer": "Saccadic"
  },
  {
    "q": "Which of the following letters of the alphabet cannot be found in the Library of Congress Classification Scheme?",
    "options": [
      "Letter C",
      "Letter G",
      "Letter O",
      "Letter S"
    ],
    "answer": "Letter O"
  },
  {
    "q": "Arrangement of materials on the shelves is done using _______",
    "options": [
      "Classification scheme",
      "Nominal roll",
      "Planned steps",
      "Catalogue"
    ],
    "answer": "Classification scheme"
  },
  {
    "q": "When a book is written by more than six authors, a researcher using the APA referencing style should _______ when citing in the reference list.",
    "options": [
      "Provide the name of the first three authors",
      "List all the authors",
      "Not list any other names after the sixth author but write et al. in their place",
      "Write the names of the first six authors"
    ],
    "answer": "Not list any other names after the sixth author but write et al. in their place"
  },
  {
    "q": "Yes/No questions are naturally asked using the _______ tune.",
    "options": [
      "Fall-rise",
      "Rise-fall",
      "Falling",
      "Rising"
    ],
    "answer": "Rising"
  },
  {
    "q": "_______ is the plural of datum.",
    "options": [
      "Data",
      "Information",
      "System",
      "Datus"
    ],
    "answer": "Data"
  },
  {
    "q": "I saw them across the road. The expression 'across the road' can be described as a ______.",
    "options": [
      "Noun phrase",
      "Adjective phrase",
      "Prepositional phrase",
      "Verb phrase"
    ],
    "answer": "Prepositional phrase"
  },
  {
    "q": "Information processing involves the following except ______.",
    "options": [
      "Recording",
      "Encoding",
      "Storage",
      "Retrieval"
    ],
    "answer": "Recording"
  },
  {
    "q": "A/an _______ is a combination of ideas from one paragraph to another, that creates a united whole.",
    "options": [
      "Essay",
      "Text",
      "Sentence",
      "Paragraph"
    ],
    "answer": "Essay"
  },
  {
    "q": "SQ3R refers to ______.",
    "options": [
      "See, Question 3R",
      "See, Query, 3R",
      "Sign, Query, 3R",
      "Survey, Question, 3R"
    ],
    "answer": "Survey, Question, 3R"
  },
  {
    "q": "One of the following is NOT true.",
    "options": [
      "Through reading, you improve upon your listening skills",
      "Through reading, you diminish your speech ability",
      "Through reading, you enlarge your vocabulary",
      "Through reading, you improve your writing skills"
    ],
    "answer": "Through reading, you diminish your speech ability"
  },
  {
    "q": "When a long word is shortened to make it less awkward for speech, it is referred to as a ______.",
    "options": [
      "Clipped",
      "Crimped",
      "Chipped",
      "Chopped"
    ],
    "answer": "Clipped"
  },
  {
    "q": "All but one of these are Indefinite pronouns.",
    "options": [
      "Several",
      "Someone",
      "Anyone",
      "Everyone"
    ],
    "answer": "Several"
  },
  {
    "q": "Combination of letters and figures indicating the classes of a book in a library is known as ______.",
    "options": [
      "Book indicator",
      "Call mark",
      "Book figure",
      "Marker"
    ],
    "answer": "Call mark"
  },
  {
    "q": "Which of the reference styles excludes the year of publication in the in-text citation?",
    "options": [
      "MLA",
      "MPA",
      "APA",
      "Harvard"
    ],
    "answer": "MLA"
  },
  {
    "q": "One of the following is not a distinction made between vowels.",
    "options": [
      "High/low",
      "Rounded/around",
      "Long/short",
      "Open/closed"
    ],
    "answer": "Rounded/around"
  },
  {
    "q": "An example of a search engine is ______.",
    "options": [
      "Database",
      "Internet Explorer",
      "Mozilla",
      "Google"
    ],
    "answer": "Google"
  },
  {
    "q": "Effective use of the library resources requires ______.",
    "options": [
      "Punctuality",
      "Maturity",
      "Smartness",
      "Search strategies"
    ],
    "answer": "Search strategies"
  },
  {
    "q": "A three-consonant onset obligatorily has _______ as the first consonant.",
    "options": [
      "/p/",
      "/s/",
      "/k/",
      "/t/"
    ],
    "answer": "/s/"
  },
  {
    "q": "A finite clause contains one of the following:",
    "options": [
      "No verb at all",
      "A verb that changes",
      "Two or more verbs",
      "A verb that remains unchanging"
    ],
    "answer": "A verb that changes"
  },
  {
    "q": "_______ theory is a phonetic theory of syllable description.",
    "options": [
      "Prominence",
      "Diffusion",
      "Osmosis",
      "Synchronic"
    ],
    "answer": "Prominence"
  },
  {
    "q": "_______ is a type of index.",
    "options": [
      "All",
      "Book index",
      "Periodical index",
      "Newspaper index"
    ],
    "answer": "All"
  },
  {
    "q": "A good essay should contain ______.",
    "options": [
      "A variation of long and short paragraphs",
      "Predominantly short paragraphs",
      "Predominantly long paragraphs",
      "Predominantly one-sentence paragraphs"
    ],
    "answer": "A variation of long and short paragraphs"
  },
  {
    "q": "One of the following is not a type of essay:",
    "options": [
      "Analytical",
      "Narrative",
      "Experimental",
      "Descriptive"
    ],
    "answer": "Experimental"
  },
  {
    "q": "/s/, /t/ and /n/ are related based on their _______ of articulation.",
    "options": [
      "Length",
      "Place",
      "Manner",
      "Nature"
    ],
    "answer": "Place"
  },
  {
    "q": "A student that has committed plagiarism can be ______.",
    "options": [
      "Promoted",
      "Jailed",
      "Given an award",
      "Dismissed from school"
    ],
    "answer": "Dismissed from school"
  },
  {
    "q": "Vowels cannot be articulated when the lips are ______.",
    "options": [
      "Neutral",
      "Spread",
      "Rounded",
      "Pursed"
    ],
    "answer": "Pursed"
  },
  {
    "q": "_______, according to experts, produces the strongest effect on stress placement than all the other features.",
    "options": [
      "Pitch",
      "Vowel quality",
      "Loudness",
      "Length"
    ],
    "answer": "Pitch"
  },
  {
    "q": "Which clause pattern is reflected in this sentence: Kofi became the president.",
    "options": [
      "SVOC",
      "SVA",
      "SVOO",
      "SVC"
    ],
    "answer": "SVC"
  },
  {
    "q": "An index serves as _______ to required information.",
    "options": [
      "Indicator",
      "None",
      "Pointer and indicator",
      "Pointer"
    ],
    "answer": "Pointer and indicator"
  },
  {
    "q": "The largest grammatical unit in English is the ______ and the smallest is the ______.",
    "options": [
      "Morpheme — sentence",
      "Morpheme — lexis",
      "Morpheme — paragraph",
      "Morpheme — syntax"
    ],
    "answer": "Morpheme — sentence"
  },
  {
    "q": "A passage written in a technical or difficult language is best read ______.",
    "options": [
      "At a fast pace only once",
      "By scholars",
      "At a slow pace",
      "None of the above"
    ],
    "answer": "At a slow pace"
  },
  {
    "q": "_______ occurs when the meaning of a word depends on its environment and usage.",
    "options": [
      "Pronunciation",
      "Assimilation",
      "Opposition",
      "Connotation"
    ],
    "answer": "Connotation"
  },
  {
    "q": "_______ is not a bad reading habit.",
    "options": [
      "Word-by-word reading",
      "Moving the head from side to side",
      "Vocalisation",
      "Having a wide span of recognition"
    ],
    "answer": "Having a wide span of recognition"
  },
  {
    "q": "One of the attributes of information is ______.",
    "options": [
      "Citation",
      "Non-reliability",
      "Printing",
      "Relevance"
    ],
    "answer": "Relevance"
  },
  {
    "q": "Any information retrieved from the Internet can be considered accurate.",
    "options": [
      "False",
      "Yes",
      "True",
      "Partially true"
    ],
    "answer": "False"
  },
  {
    "q": "When the intonation of a sentence identifies that sentence as a statement, question, etc., it is said to perform a/an ______ function.",
    "options": [
      "Grammatical",
      "Discourse",
      "Accentual",
      "Attitudinal"
    ],
    "answer": "Grammatical"
  },
  {
    "q": "Below are the steps involved in summarising a text; arrange them in the appropriate order: i. Express the contents of the text in your own words ii. Read to find the basic ideas iii. Compare your summary with the original text iv. Read to find the essentials",
    "options": [
      "ii, iv, i, iii",
      "iv, iii, ii, i",
      "i, iii, ii, iv",
      "i, ii, iii, iv"
    ],
    "answer": "ii, iv, i, iii"
  },
  {
    "q": "A ______ can be consulted for instruction on how to do things.",
    "options": [
      "Manual",
      "Newsletter",
      "Lecture note",
      "Card"
    ],
    "answer": "Manual"
  },
  {
    "q": "Identify the interrogative sentence:",
    "options": [
      "Let's go to France",
      "Take the bus home",
      "I don't believe that!",
      "Where are you going?"
    ],
    "answer": "Where are you going?"
  },
  {
    "q": "All but one of the words listed below is an example of Neologism:",
    "options": [
      "Brunch",
      "Atmosphere",
      "Webinar",
      "Malware"
    ],
    "answer": "Atmosphere"
  },
  {
    "q": "When the meaning of a word is considered in isolation, it is known as ______ meaning.",
    "options": [
      "Denotative",
      "Connotative",
      "Complex",
      "Objective"
    ],
    "answer": "Denotative"
  },
  {
    "q": "Radio, Tape-recorder, Gramophone, and Audio cassette player are examples of _______.",
    "options": [
      "Visual materials",
      "Audio materials",
      "Electronic material",
      "Audio-visual materials"
    ],
    "answer": "Audio materials"
  },
  {
    "q": "Identify the misspelled word below:",
    "options": [
      "Sphinx",
      "Harrassment",
      "Embarrassment",
      "Repertoire"
    ],
    "answer": "Harrassment"
  },
  {
    "q": "Which of the following is correct?",
    "options": [
      "The responsibility is their's",
      "The dog wagged its tail",
      "The dog wagged it's tail",
      "The reward is your's"
    ],
    "answer": "The dog wagged its tail"
  },
  {
    "q": "Which of the following is true?",
    "options": [
      "We read for knowledge acquisition only",
      "We read only for pleasure",
      "None of the above",
      "We read only for exams"
    ],
    "answer": "None of the above"
  },
  {
    "q": "For some reason, I _______ a change in her attitude.",
    "options": [
      "Precieved",
      "Perceived",
      "Percieved",
      "Perceved"
    ],
    "answer": "Perceived"
  },
  {
    "q": "Mixed notation refers to the use of letters of the alphabet as well as ______.",
    "options": [
      "Roman numbers",
      "Arabic numerals",
      "Arabic alphabets",
      "Roman numerals"
    ],
    "answer": "Arabic numerals"
  },
  {
    "q": "Meta Search involves use of _______.",
    "options": [
      "Advanced search engines",
      "Meta search engines",
      "Basic search engines",
      "Primary search engines"
    ],
    "answer": "Meta search engines"
  },
  {
    "q": "One of the following is a reading technique.",
    "options": [
      "RSTPQ",
      "PQRST",
      "QRSTP",
      "STPQR"
    ],
    "answer": "PQRST"
  },
  {
    "q": "In reviewing an item you have read, one of the following is not necessary.",
    "options": [
      "References",
      "The highlighted items",
      "The annotated items",
      "The heading"
    ],
    "answer": "References"
  },
  {
    "q": "Which of the following is not a standard reading technique?",
    "options": [
      "3S3R",
      "3RQS",
      "PQRST",
      "SQ3R"
    ],
    "answer": "3RQS"
  },
  {
    "q": "In the word 'janitor', stress falls on the _______ syllable.",
    "options": [
      "Final",
      "Medial",
      "Initial",
      "None of the above"
    ],
    "answer": "Initial"
  },
  {
    "q": "The category of words to which new words can always be added is called _______.",
    "options": [
      "Grammatical words",
      "Open class words",
      "Lexical class words",
      "Suffixation words"
    ],
    "answer": "Open class words"
  },
  {
    "q": "She walks briskly. Identify the adverb type.",
    "options": [
      "Adverb of degree",
      "Adverb of frequency",
      "Adverb of manner",
      "Adverb of place"
    ],
    "answer": "Adverb of manner"
  },
  {
    "q": "The simple present tense is used to indicate _______.",
    "options": [
      "States",
      "Present",
      "Irregularity",
      "Regularity"
    ],
    "answer": "Regularity"
  },
  {
    "q": "One of the following is correct about reading:",
    "options": [
      "An individual can read 600 words per minute",
      "We need to read everything",
      "Everything can be read the same way",
      "Everything on a page is equally important"
    ],
    "answer": "An individual can read 600 words per minute"
  },
  {
    "q": "Information can be evaluated using the following criteria EXCEPT _______.",
    "options": [
      "Relevancy",
      "Currency",
      "Size",
      "Accuracy"
    ],
    "answer": "Size"
  },
  {
    "q": "The mechanism for accessing information in the library is through both _______ and _______.",
    "options": [
      "Google & search engines",
      "Book catalogue",
      "Mobile phone & accessories",
      "Traditional catalogue & OPAC"
    ],
    "answer": "Traditional catalogue & OPAC"
  },
  {
    "q": "When one's intonation betrays their emotion on the subject matter, it is said to perform a/an _______.",
    "options": [
      "Grammatical",
      "Discourse",
      "Attitudinal",
      "Accentual"
    ],
    "answer": "Attitudinal"
  },
  {
    "q": "High vowels are also described as __________ vowels.",
    "options": [
      "Close",
      "Long",
      "Rounded",
      "Open"
    ],
    "answer": "Close"
  },
  {
    "q": "__________ is not a bilabial sound.",
    "options": [
      "/m/",
      "/b/",
      "/f/",
      "/p/"
    ],
    "answer": "/f/"
  },
  {
    "q": "Daniel is an architect. The underlined is the __________.",
    "options": [
      "Direct object of the verb",
      "Object complement",
      "Subject complement",
      "Prepositional complement"
    ],
    "answer": "Subject complement"
  },
  {
    "q": "When intonation aids turn-taking, it performs a/an __________ function.",
    "options": [
      "Attitudinal",
      "Accentual",
      "Discourse",
      "Grammatical"
    ],
    "answer": "Discourse"
  },
  {
    "q": "The asterisk sign (*) in a search is known as:",
    "options": [
      "Wild card",
      "Simple search",
      "Truncation",
      "Phrase search"
    ],
    "answer": "Truncation"
  },
  {
    "q": "Faculty handbook is an example of a small ready reference source.",
    "options": [
      "False",
      "True",
      "Partially false",
      "No"
    ],
    "answer": "True"
  },
  {
    "q": "'OR' is used as a search strategy when a user wants to ______ the search.",
    "options": [
      "Narrow",
      "Develop",
      "Broaden",
      "Limit"
    ],
    "answer": "Broaden"
  },
  {
    "q": "Law books in the University of Lagos Library can be found in:",
    "options": [
      "Class M",
      "Class H",
      "Class G",
      "Class K"
    ],
    "answer": "Class K"
  },
  {
    "q": "Every complex word contains a/an ______.",
    "options": [
      "Affix",
      "Verb",
      "Prefix",
      "Noun"
    ],
    "answer": "Affix"
  },
  {
    "q": "The sentence: 'They lost some extremely valuable documents in the fire.' The expression 'extremely valuable' is an example of a/an:",
    "options": [
      "Prepositional phrase",
      "Adjective phrase",
      "Noun phrase",
      "Adverbial phrase"
    ],
    "answer": "Adjective phrase"
  },
  {
    "q": "Libraries perform all of these functions EXCEPT:",
    "options": [
      "Organisation",
      "Acquisition",
      "Preservation",
      "Book selling"
    ],
    "answer": "Book selling"
  },
  {
    "q": "A biography is:",
    "options": [
      "A detailed description of a person's life written by someone else",
      "An account of a person's life written by himself or herself",
      "Annual book",
      "General book"
    ],
    "answer": "A detailed description of a person's life written by someone else"
  },
  {
    "q": "Unity in a paragraph suggests:",
    "options": [
      "Brevity",
      "Singularity of focus",
      "Elocution",
      "Connection with other paragraphs"
    ],
    "answer": "Singularity of focus"
  },
  {
    "q": "Which one of the following is not a Word Formation Strategy?",
    "options": [
      "Suffixing",
      "Clipping",
      "Blending",
      "Coining"
    ],
    "answer": "Coining"
  },
  {
    "q": "Regular/normal conversations with people usually attract ______ listening.",
    "options": [
      "Total",
      "Informal",
      "Partial",
      "Formal"
    ],
    "answer": "Informal"
  },
  {
    "q": "Closing or rising diphthongs never end in:",
    "options": [
      "/i/",
      "None of the above",
      "/u/",
      "The schwa"
    ],
    "answer": "The schwa"
  },
  {
    "q": "Publications issued in successive parts, at regular intervals, and intended to be continued indefinitely are:",
    "options": [
      "Collective report",
      "None",
      "Serials report",
      "Serials collection"
    ],
    "answer": "Serials collection"
  },
  {
    "q": "Which of the following is not a mark of a serious student?",
    "options": [
      "Avoiding distractions while reading",
      "Reading study materials anywhere",
      "Having a reading timetable",
      "Reading at a specific time and place"
    ],
    "answer": "Reading study materials anywhere"
  },
  {
    "q": "Wow! Oh no! Watch it! are:",
    "options": [
      "Conjunctions",
      "Prepositions",
      "Interjections",
      "Nouns"
    ],
    "answer": "Interjections"
  },
  {
    "q": "Conjunctive adverbs function in a sentence to:",
    "options": [
      "Clarify the relationship between clauses of concurrent status in a sentence",
      "Clarify the relationship between clauses of equal status in a sentence",
      "Clarify the relationship between clauses of unequal status in a sentence",
      "Magnify the relationship between clauses of concurrent status in a sentence"
    ],
    "answer": "Clarify the relationship between clauses of equal status in a sentence"
  },
  {
    "q": "Stress prediction based on syllable structure is basically:",
    "options": [
      "Semantic",
      "Syntactic",
      "Morphological",
      "Phonological"
    ],
    "answer": "Phonological"
  },
  {
    "q": "The ______ criterion focuses on the word's part of speech.",
    "options": [
      "Morphological",
      "Phonological",
      "Syntactic",
      "Semantic"
    ],
    "answer": "Syntactic"
  },
  {
    "q": "Letter T is assigned to books on ________ in the Library of Congress Classification Scheme.",
    "options": [
      "Science",
      "Arts",
      "Technology",
      "Medicine"
    ],
    "answer": "Technology"
  },
  {
    "q": "A/an _______ is a unit of any composition comprising a collection of related sentences dealing with a single topic.",
    "options": [
      "Paragraph",
      "Essay",
      "Sentence",
      "Text"
    ],
    "answer": "Paragraph"
  },
  {
    "q": "The colon is used in the following situations EXCEPT:",
    "options": [
      "To introduce a list as part of a sentence",
      "To introduce the name of the publisher in a text",
      "To introduce direct speeches in some contexts",
      "To break a title into two parts"
    ],
    "answer": "To introduce the name of the publisher in a text"
  },
  {
    "q": "One can search the library catalogue for information materials using all these EXCEPT:",
    "options": [
      "Subject",
      "Author",
      "Language",
      "Title"
    ],
    "answer": "Language"
  },
  {
    "q": "The banks which had failed to comply were sanctioned. The underlined word in this sentence is:",
    "options": [
      "Relative clause",
      "Undefined relative clause",
      "Paired clause",
      "Restrictive relative clause"
    ],
    "answer": "Restrictive relative clause"
  },
  {
    "q": "The first reading of a passage is often targeted at:",
    "options": [
      "Isolating direct points from indirect ones",
      "Isolating subjective points from objective ones",
      "Obtaining a general impression of the central idea",
      "Isolating the main ideas from the minor ones"
    ],
    "answer": "Obtaining a general impression of the central idea"
  },
  {
    "q": "A syllable with a CV structure is said to be ______.",
    "options": [
      "Strong",
      "Open",
      "Weak",
      "Close"
    ],
    "answer": "Open"
  },
  {
    "q": "__________ provide information on places and physical features.",
    "options": [
      "Bibliographical source",
      "None",
      "Geographical source",
      "Fact source"
    ],
    "answer": "Geographical source"
  },
  {
    "q": "The main kinds of electronic materials in most libraries are:",
    "options": [
      "Pamphlets and videotapes",
      "Pamphlets and cassettes",
      "E-books and e-periodicals",
      "Cards and newspapers"
    ],
    "answer": "E-books and e-periodicals"
  },
  {
    "q": "A vertical superscript mark placed before a syllable in a word marks that syllable as ______.",
    "options": [
      "Silent",
      "Open",
      "Optional",
      "Stressed"
    ],
    "answer": "Stressed"
  },
  {
    "q": "A comprehension passage is best understood when it is read ______.",
    "options": [
      "Thrice",
      "Twice",
      "Once",
      "More than once"
    ],
    "answer": "More than once"
  },
  {
    "q": "In OK4R, which of the following is not one of the R's?",
    "options": [
      "Read",
      "Reflect",
      "Repeat",
      "Recall"
    ],
    "answer": "Repeat"
  },
  {
    "q": "The University of Lagos Library has newspapers dating as far back as:",
    "options": [
      "1860",
      "1920",
      "1930",
      "1960"
    ],
    "answer": "1860"
  },
  {
    "q": "Which of these is not a basic clause pattern in simple English sentences?",
    "options": [
      "SVA",
      "SVOA",
      "SVCC",
      "SVO"
    ],
    "answer": "SVCC"
  },
  {
    "q": "One of the following is not necessary when writing an argument:",
    "options": [
      "None of the above",
      "Use of details",
      "Appeal to emotion",
      "Creation of a mental picture"
    ],
    "answer": "Creation of a mental picture"
  },
  {
    "q": "Arrangement in a library catalogue is in ________ order.",
    "options": [
      "Chronological",
      "Triangular",
      "Alphabetical",
      "Decimal"
    ],
    "answer": "Alphabetical"
  },
  {
    "q": "Which of the following sentences uses an intransitive verb?",
    "options": [
      "Your house is too far.",
      "My sister ran away.",
      "The woman ate the food.",
      "The baby cried."
    ],
    "answer": "The baby cried."
  },
  {
    "q": "Which coordinating conjunction is not used in compound sentences?",
    "options": [
      "And",
      "So that",
      "Yet",
      "But"
    ],
    "answer": "So that"
  },
  {
    "q": "Interrogative sentences __________________",
    "options": [
      "Give commands",
      "Make statements",
      "Express strong emotion",
      "Ask questions"
    ],
    "answer": "Ask questions"
  },
  {
    "q": "The clause introduced by a relative pronoun is known as:",
    "options": [
      "An adjectival clause",
      "Pronoun clause",
      "Verbal clause",
      "An adverbial clause"
    ],
    "answer": "An adjectival clause"
  },
  {
    "q": "Voicing occurs as a result of the ________ of the vocal folds.",
    "options": [
      "Vibration",
      "Relaxation",
      "Agitation",
      "Separation"
    ],
    "answer": "Vibration"
  },
  {
    "q": "A verb which always occurs with an object is a/an _____________ verb.",
    "options": [
      "Transitive",
      "Primary auxiliary",
      "Modal auxiliary",
      "Intransitive"
    ],
    "answer": "Transitive"
  },
  {
    "q": "__________ is referred to as the meat of the essay.",
    "options": [
      "Expression",
      "Organization",
      "Mechanics",
      "Content"
    ],
    "answer": "Content"
  },
  {
    "q": "The acronym OPAC means:",
    "options": [
      "Online Public Access Catalogue",
      "Online Primary Access Catalogue",
      "Online Private Access Catalogue",
      "None"
    ],
    "answer": "Online Public Access Catalogue"
  },
  {
    "q": "Apostrophes are used ________.",
    "options": [
      "To form plurals",
      "For contractions",
      "For transitivity",
      "For epithesis"
    ],
    "answer": "For contractions"
  },
  {
    "q": "An open glottis results in the production of ________.",
    "options": [
      "Consonants",
      "Voiceless sounds",
      "Vowels",
      "Voiced sounds"
    ],
    "answer": "Voiceless sounds"
  },
  {
    "q": "Directories, handbooks, yearbooks, and almanacs are ________ sources.",
    "options": [
      "None",
      "Geographical sources",
      "Fact sources",
      "Bibliographical sources"
    ],
    "answer": "Fact sources"
  },
  {
    "q": "How a reading material is read is determined by ________.",
    "options": [
      "The reader",
      "The author",
      "The publishers",
      "Its nature"
    ],
    "answer": "Its nature"
  },
  {
    "q": "Which subordinating conjunction cannot be used to introduce an adverb clause?",
    "options": [
      "Nevertheless",
      "If",
      "When",
      "Although"
    ],
    "answer": "Nevertheless"
  },
  {
    "q": "One of these does not appear in the reference list:",
    "options": [
      "Page",
      "Author's name",
      "Title of a work",
      "Keyword"
    ],
    "answer": "Keyword"
  },
  {
    "q": "Africana collection is found in ________.",
    "options": [
      "Reserved collection",
      "Serials",
      "Gandhi Library",
      "Reference collection"
    ],
    "answer": "Gandhi Library"
  },
  {
    "q": "Note-taking complements __________________",
    "options": [
      "none of the above",
      "listening",
      "speaking",
      "writing"
    ],
    "answer": "listening"
  },
  {
    "q": "A question mark is not used at the end of ________.",
    "options": [
      "none of the above",
      "all of the above",
      "a direct question",
      "an indirect question"
    ],
    "answer": "an indirect question"
  },
  {
    "q": "How many forms do state-of-being verbs and action verbs have?",
    "options": [
      "2",
      "7",
      "5",
      "9"
    ],
    "answer": "5"
  },
  {
    "q": "One of the following is not a linking device:",
    "options": [
      "however",
      "finally",
      "Because",
      "furthermore"
    ],
    "answer": "Because"
  },
  {
    "q": "Speech defect is a ________ condition hampering effective listening.",
    "options": [
      "psychological",
      "spiritual",
      "physical",
      "physiological"
    ],
    "answer": "physiological"
  },
  {
    "q": "________________ is often called the awkward stage.",
    "options": [
      "Adolescence",
      "Adolessents",
      "Adolscence",
      "Adolescense"
    ],
    "answer": "Adolescence"
  },
  {
    "q": "When keywords are embedded in quotes, the type of search performed is ________.",
    "options": [
      "Boolean search",
      "Basic search",
      "Subject search",
      "Phrase search"
    ],
    "answer": "Phrase search"
  },
  {
    "q": "Which of the following words contains three sounds?",
    "options": [
      "trust",
      "thoughts",
      "cheap",
      "frog"
    ],
    "answer": "cheap"
  },
  {
    "q": "Index is found at the ________.",
    "options": [
      "Front of a book",
      "Middle of the book",
      "Centre of the book",
      "Back of book"
    ],
    "answer": "Back of book"
  },
  {
    "q": "The __________ essay emphasizes character and setting.",
    "options": [
      "narrative",
      "descriptive",
      "persuasive",
      "analytical"
    ],
    "answer": "narrative"
  },
  {
    "q": "________________ is a system of identifying and marking out important ideas or parts in a text being read.",
    "options": [
      "study reading",
      "paraphrasing",
      "underlining",
      "highlighting"
    ],
    "answer": "highlighting"
  },
  {
    "q": "The schwa is a ________ vowel.",
    "options": [
      "high",
      "back",
      "central",
      "low"
    ],
    "answer": "central"
  },
  {
    "q": "Based on the length of storage of information, memory is classified into ______",
    "options": [
      "long and short-term",
      "transient and permanent",
      "visible and invisible",
      "variable and invariable"
    ],
    "answer": "long and short-term"
  },
  {
    "q": "In scanning a reading material, the reader seeks to ____________________",
    "options": [
      "get specific information",
      "have a general idea of the topic",
      "ensure grammaticality",
      "check plagiarism"
    ],
    "answer": "get specific information"
  },
  {
    "q": "A secondary source is one that _______ and _______ a primary source.",
    "options": [
      "Critiques and disqualify",
      "Reviews and manipulates",
      "All",
      "Analyzes & explains"
    ],
    "answer": "Analyzes & explains"
  },
  {
    "q": "________________ is a receptive skill.",
    "options": [
      "writing",
      "reading",
      "speaking",
      "listening"
    ],
    "answer": "reading"
  },
  {
    "q": "The lungs are housed in the ________.",
    "options": [
      "Larynx",
      "Spinal cord",
      "Thorax",
      "Rib cage"
    ],
    "answer": "Thorax"
  },
  {
    "q": "What is the suitable reference source for obtaining information about background and current information on any field of study?",
    "options": [
      "Directory",
      "Encyclopaedia",
      "Year book",
      "Gazetteer"
    ],
    "answer": "Encyclopaedia"
  },
  {
    "q": "__________ are reference materials that provide spellings, meanings, pronunciation and synonyms of words.",
    "options": [
      "Newspaper",
      "Index",
      "Encyclopaedias",
      "Dictionaries"
    ],
    "answer": "Dictionaries"
  },
  {
    "q": "An offence of self-plagiarism is said to have been committed if ________.",
    "options": [
      "You copy from your previous assignment for a new assignment without acknowledgment",
      "You copy from your lecturer's handout without acknowledgment",
      "None of the above",
      "You copy from the internet without acknowledgment"
    ],
    "answer": "You copy from your previous assignment for a new assignment without acknowledgment"
  },
  {
    "q": "-eer in 'engineer' and -aire in 'millionaire' are examples of ________________ affixes.",
    "options": [
      "stress-conserving",
      "stress-moving",
      "stress-neutral",
      "stress-bearing"
    ],
    "answer": "stress-bearing"
  },
  {
    "q": "Which stress level is marked with a subscript?",
    "options": [
      "Primary",
      "Tertiary",
      "Secondary",
      "Zero"
    ],
    "answer": "Secondary"
  },
  {
    "q": "Affixes that cause stress to move from one syllable to another are called:",
    "options": [
      "Stress-bearing",
      "Stress-conserving",
      "Stress-neutral",
      "Stress-moving"
    ],
    "answer": "Stress-moving"
  },
  {
    "q": "How many morphemes are in the word 'boyish'?",
    "options": [
      "2",
      "4",
      "6",
      "1"
    ],
    "answer": "2"
  },
  {
    "q": "Which punctuation is used to separate phrases and clauses in a series within a sentence?",
    "options": [
      "Semi-colon",
      "Comma",
      "Colon",
      "Hyphen"
    ],
    "answer": "Comma"
  },
  {
    "q": "Which of the following is not a subordinating conjunction?",
    "options": [
      "For",
      "Than",
      "That",
      "Even if"
    ],
    "answer": "For"
  },
  {
    "q": "Listening is not the ability to ________ the meaning of what is said.",
    "options": [
      "Perceive",
      "Receive",
      "Denounce",
      "Decode"
    ],
    "answer": "Denounce"
  },
  {
    "q": "In ________, we read to get the overall idea of a text.",
    "options": [
      "Scanning",
      "Spinning",
      "Skimming",
      "Study reading"
    ],
    "answer": "Skimming"
  },
  {
    "q": "A well-developed paragraph contains the following except _______.",
    "options": [
      "Definition of terms",
      "Examples and illustrations",
      "Evaluation of cause and effect",
      "Sentence fragments"
    ],
    "answer": "Sentence fragments"
  },
  {
    "q": "The prefix -un in the word 'unreliable' can be described as a ________ morpheme.",
    "options": [
      "Bound",
      "Free",
      "Inflectional",
      "Derivational"
    ],
    "answer": "Derivational"
  },
  {
    "q": "The part of a word to which other elements can be added is called ________.",
    "options": [
      "Prefix",
      "Root or stem",
      "Suffix",
      "Phrase"
    ],
    "answer": "Root or stem"
  },
  {
    "q": "Index may be published as part of a book or separately.",
    "options": [
      "False",
      "Partially true",
      "Partially false",
      "True"
    ],
    "answer": "True"
  },
  {
    "q": "Analytical essays focus on the following except ________.",
    "options": [
      "Identification of an issue",
      "Providing a sequential or chronological account",
      "Examination of the issue",
      "Assessment of the implication for human existence"
    ],
    "answer": "Providing a sequential or chronological account"
  },
  {
    "q": "Which of the following is not a post-lecture activity?",
    "options": [
      "Revision",
      "Review",
      "Disposal",
      "Summary"
    ],
    "answer": "Disposal"
  },
  {
    "q": "Self-plagiarism occurs when you:",
    "options": [
      "Copy from your lecturer's handout without acknowledgment",
      "Copy from the internet without acknowledgment",
      "None of the above",
      "Copy from your previous assignment for a new one without acknowledgment"
    ],
    "answer": "Copy from your previous assignment for a new one without acknowledgment"
  },
  {
    "q": "All of the following are referencing styles except:",
    "options": [
      "MLA",
      "ALA",
      "Harvard",
      "NLA"
    ],
    "answer": "ALA"
  },
  {
    "q": "What is the maximum number of consonants allowed at the beginning of an English syllable?",
    "options": [
      "5",
      "6",
      "3",
      "4"
    ],
    "answer": "3"
  },
  {
    "q": "Which of the following rarely occurs in unstressed syllables?",
    "options": [
      "Syllabic consonants",
      "Short vowels",
      "Diphthongs",
      "The schwa"
    ],
    "answer": "Diphthongs"
  },
  {
    "q": "A/an ______ paragraph explains how or why something happens.",
    "options": [
      "Explanation",
      "Sequence",
      "Choice",
      "Definition"
    ],
    "answer": "Explanation"
  },
  {
    "q": "Biographies and autobiographies are classified under which type of essay?",
    "options": [
      "Analytical",
      "Experimental",
      "Narrative",
      "Descriptive"
    ],
    "answer": "Narrative"
  },
  {
    "q": "The first step in reading a passage is to:",
    "options": [
      "Preview it",
      "Appreciate it",
      "Summarize it",
      "Edit it"
    ],
    "answer": "Preview it"
  },
  {
    "q": "The main purpose of reading is to ______ written material.",
    "options": [
      "Comprehend",
      "Identify",
      "Buy",
      "Practice"
    ],
    "answer": "Comprehend"
  },
  {
    "q": "To develop a paragraph effectively, a ______-step process is recommended.",
    "options": [
      "5",
      "3",
      "7",
      "1"
    ],
    "answer": "5"
  },
  {
    "q": "'And' is used as a Boolean operator when you want to ________ your search results.",
    "options": [
      "Widen",
      "Define",
      "Specify",
      "Harvest"
    ],
    "answer": "Specify"
  },
  {
    "q": "'un' in the word unfaithful is an example of a ________.",
    "options": [
      "Conjunct",
      "Subjunction",
      "Suffix",
      "Prefix"
    ],
    "answer": "Prefix"
  },
  {
    "q": "One of the following is not a criterion for predicting stress.",
    "options": [
      "Semantic",
      "Phonological",
      "Syntactic",
      "Morphological"
    ],
    "answer": "Semantic"
  },
  {
    "q": "__________ refers to the rise and fall of the tone of the voice.",
    "options": [
      "Rhythm",
      "Intonation",
      "Stress",
      "Intensity"
    ],
    "answer": "Intonation"
  },
  {
    "q": "A Closed Access System of collection in a library refers to ________.",
    "options": [
      "Materials to be borrowed for home use",
      "Restricted access",
      "Materials not to be photocopied",
      "Materials to be retrieved directly by the user"
    ],
    "answer": "Restricted access"
  },
  {
    "q": "__________ is the act of using copyrighted work without permission or acknowledging the source.",
    "options": [
      "Plagiarism",
      "Dubbing",
      "Copying",
      "Copying and pasting"
    ],
    "answer": "Plagiarism"
  },
  {
    "q": "The chief aim of a narrative essay is to ________.",
    "options": [
      "Explain a process",
      "Create a mental image of something",
      "Defend a position",
      "Arouse and sustain reader's interest"
    ],
    "answer": "Arouse and sustain reader's interest"
  },
  {
    "q": "A survey of an article or chapter in a book does not take ________ into consideration.",
    "options": [
      "The introduction and conclusion",
      "Its title",
      "The topic sentences",
      "The blurb"
    ],
    "answer": "The blurb"
  },
  {
    "q": "The following are listed electronic information resources in UNILAG Library website EXCEPT ________.",
    "options": [
      "Science Direct, Dogpile & Google",
      "Yahoo, Google & OPAC",
      "Google, HINARI & AJOL",
      "Science Direct, Ebscohost & Ebrary"
    ],
    "answer": "Science Direct, Dogpile & Google"
  },
  {
    "q": "Which of these does not belong in this group? (Proper nouns)",
    "options": [
      "Kaduna",
      "Ocean",
      "Mathematics",
      "John"
    ],
    "answer": "Ocean"
  },
  {
    "q": "In speech production, __________ of the human body is involved.",
    "options": [
      "Three quarters",
      "The whole",
      "A quarter",
      "Half"
    ],
    "answer": "The whole"
  }

        ]


}

@app.route('/')
def index():
    app.logger.debug('index session contents: %r', dict(session))
    expires = None
    if 'expires_at' in session:
        try:
            expires = datetime.fromtimestamp(session['expires_at']).isoformat()
        except Exception:
            expires = session.get('expires_at')
    return render_template('index.html', subjects=QUESTIONS.keys(), expires_display=expires)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # clear anything leftover from a previous session (old expiry strings etc.)
    if request.method == 'GET':
        session.clear()
        # also clear the client cookie by sending an empty one
        from flask import make_response
        resp = make_response(render_template('login.html'))
        resp.set_cookie('session', '', expires=0)
        return resp
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Please enter a name to log in.')
            return redirect(url_for('login'))
        session['username'] = name
        now = datetime.utcnow()
        session['start_time'] = now.isoformat()
        # store expiration as a timestamp (seconds since epoch) to avoid
        # timezone parsing issues in JavaScript
        session['expires_at'] = (now + timedelta(minutes=30)).timestamp()
        # debug output
        app.logger.debug('login session contents: %r', dict(session))
        flash(f'Logged in as {name}. You have 30 minutes and up to 60 questions per subject.')
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/quiz/<subject>', methods=['GET', 'POST'])
def quiz(subject):
    if subject not in QUESTIONS:
        return redirect(url_for('index'))
    # require login
    if 'username' not in session:
        flash('Please log in before taking a quiz.')
        return redirect(url_for('login'))

    # check expiry (expires stored as timestamp) and normalize if necessary
    expires = session.get('expires_at')
    if isinstance(expires, str):
        try:
            expires = float(expires)
            session['expires_at'] = expires
        except ValueError:
            expires = None
    if expires:
        try:
            now_ts = datetime.utcnow().timestamp()
            if now_ts > expires:
                session.clear()
                return render_template('timeout.html')
        except Exception as e:
            app.logger.error('expiry check error: %s', e)
            session.clear()
            return render_template('timeout.html')

    # prepare questions for this quiz request; statelessly sample indices and send them in the form
    all_q = QUESTIONS[subject]
    if request.method == 'GET':
        count = min(60, len(all_q))
        indices = random.sample(range(len(all_q)), count) if len(all_q) > count else list(range(len(all_q)))
        questions = [all_q[i] for i in indices]
    else:  # POST
        # indices are posted back as JSON string
        import json as _json
        indices_str = request.form.get('indices', '[]')
        try:
            indices = _json.loads(indices_str)
        except Exception:
            indices = []
        questions = [all_q[i] for i in indices] if indices else []

    if request.method == 'POST':
        name = session.get('username', '')
        score = 0
        answers = []
        # build a details list we can send back to the template so the student
        # can review which items they got right or wrong
        details = []
        for i, q in enumerate(questions):
            selected = request.form.get(f"q{i}")
            answers.append(selected)
            correct = (selected == q['answer'])
            if correct:
                score += 1
            details.append({
                'question': q.get('q') or q.get('question', ''),
                'options': q.get('options', []),
                'selected': selected,
                'answer': q['answer'],
                'correct': correct,
                'explanation': q.get('explanation', q.get('solution', ''))
            })
        total = len(questions)
        # compute percentage grade (scale to 100)
        percentage = round((score / total) * 100, 2) if total else 0

        # record result; keep indices so we can reconstruct later if needed
        result = {
            'name': name,
            'subject': subject,
            'score': score,
            'total': total,
            'percentage': percentage,
            'indices': indices,
            'answers': answers,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        save_result(result)
        return render_template('result.html', subject=subject, score=score, total=total,
                               percentage=percentage, name=name, details=details)

    # pass numeric expiry and the chosen indices to the template for JS handling
    return render_template('quiz.html', subject=subject, questions=questions, expires_at=session.get('expires_at'), indices=indices)



def results_file_path():
    return os.path.join(os.path.dirname(__file__), 'results.json')


def read_results():
    path = results_file_path()
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_result(entry):
    path = results_file_path()
    data = read_results()
    data.append(entry)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


@app.route('/grades')
def grades():
    results = read_results()
    return render_template('grades.html', results=results)

@app.route('/history')
def history():
    if 'username' not in session:
        flash('Please log in to view your history.')
        return redirect(url_for('login'))
    username = session.get('username')
    all_results = read_results()
    user_results = [r for r in all_results if r.get('name') == username]
    return render_template('history.html', results=user_results, username=username)

if __name__ == '__main__':
    app.run(debug=True)
