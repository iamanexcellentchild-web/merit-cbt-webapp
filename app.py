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
                'question': q['q'],
                'options': q.get('options', []),
                'selected': selected,
                'answer': q['answer'],
                'correct': correct
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
