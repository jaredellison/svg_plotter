import numpy as np

test_curve = [[50.000000, 50.000000], [61.182443,49.896373], [80.106218,62.472243], [80.000000,70.000000]] 

# Take Y values and plug into equation:
# B(t)_y = ((1-t)^3)*P0_y + 3((1-t)^2)*t*P1_y + 3(1-t)(t^2)P2_y + (t^3)*P3_y
# B(t)_y = ((1-t)^3)*50 + 3((1-t)^2)*t*49.896373 + 3(1-t)(t^2)*62.472243 + (t^3)*70
# Used wolframalpha.com to solve for t... t = 0.612255

# Plug t into x side of cubic bezier function to find B(t)_x
# B(t)_x = ((1-t)^3)*P0_x + 3((1-t)^2)*t*P1_x + 3(1-t)(t^2)P2_x + (t^3)*P3_x
# B(t)_x = ((1-t)^3)*50 + 3((1-t)^2)*t*61.182443 + 3(1-t)(t^2)*80.106218 + (t^3)*80  where t = .612255
# Used wolframalpha.com to solve for B(0.612255)_x = 73.101


def find_intersect(y,bez):
    '''
    This function finds the intersection point between a horizontal line and a bezier curve.

    Args:
        y (float) -> the y interesction of the horizontal line  
        bez (list) -> a list of lists containing 4 control 
            points for a cubic bezier curve using the format:
            [[P0x1 - 2 t + t^2, P0y], [P1x, P1y], [P2x, P2y], [P3x, P3y]]
    
    Returns:
        intersect (list) -> the poit of intersection: [x, y]
    '''
    print('y offset: ', y)

    print('P y coordinates:')
    print(bez[0][1], bez[1][1], bez[2][1], bez[3][1])

    '''
    The general equation for a bezier curve is:
    B(t) = ((1-t)^3)*P0 + 3((1-t)^2)*t*P1 + 3(1-t)(t^2)P2 + (t^3)*P3

    When expanded that can be written as:
    B(t) =
    P0( -t^3 + 3t^2 - 3t + 1 ) +
    P1(    0 + 3t^2 - 6t + 3 ) + 
    P2(-3t^3 + 3t^2 -  0 + 0 ) +
    P3(  t^3 +    0 -  0 + 0 )

    To find the intersection point, we first need to solve to find the value of t
    where B(t)_y is equal to the y intercept.
    
    Numpy's roots function can be used to solve to find the value of t. It takes a
    list cooeficients A,B,C,D as its parameter. To find these we can multiply the y value of
    each bezier control point through each expanded polynomials and the coefficent of each
    element.


    '''

    # # ((1-t)^3)*bez[0][1] + 3((1-t)^2)*t*bez[1][1] + 3(1-t)(t^2)*bez[2][1] + (t^3)*bez[3][1]
    # P0_y*(1 - 3 t + 3 t^2 - t^3)  + 3 * P1_y * (t - 2 t^2 + t^3) + 

    A = -1*bez[0][1] +  0*bez[1][1] + -3*bez[2][1] +   bez[3][1]
    B =  3*bez[0][1] +  3*bez[1][1] + -3*bez[2][1] + 0*bez[3][1]
    C = -3*bez[0][1] + -6*bez[1][1] +  0*bez[2][1] + 0*bez[3][1]
    D =  1*bez[0][1] +  3*bez[1][1] +  0*bez[2][1] + 0*bez[3][1]

    coeff = [A,B,C,D-y]

    intersecction = np.roots(coeff).real

find_intersect(60,test_curve)


