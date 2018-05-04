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

left(((1-t)^3)*50+3((1-t)^2)*t*61.182443+3(1-t)(t^2)80.106218+(t^3)*50),\ ((1-t)^3)*50+3((1-t)^2)*t*49.896373+3(1-t)(t^2)62.472243+(t^3)*50\right)

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
    P1( 3t^3 - 6t^2 + 3t + 0 ) +
    P2(-3t^3 + 3t^2 -  0 + 0 ) +
    P3(  t^3 +    0 -  0 + 0 )

    To find the intersection point, we first need to solve to find the value of t
    where B(t)_y is equal to the y intercept.
    
    Numpy's roots function can be used to solve to find the value of t. It takes a
    list cooeficients A,B,C,D as its parameter. To find these we can multiply the 
    y value of each bezier control point through each expanded polynomial and sum 
    the coefficient preceding each element to find A,B,C,D.  
    '''
    A = -1*bez[0][1] +  3*bez[1][1] + -3*bez[2][1] + 1*bez[3][1]
    B =  3*bez[0][1] + -6*bez[1][1] +  3*bez[2][1] + 0*bez[3][1]
    C = -3*bez[0][1] +  3*bez[1][1] +  0*bez[2][1] + 0*bez[3][1]
    D =  1*bez[0][1] +  0*bez[1][1] +  0*bez[2][1] + 0*bez[3][1]

    '''
    The fourth element is D-y because we need to find where the roots are zero.
    This is the quivalent of subtracting the Y offset from both sides:
    y = ((1-t)^3)*P0 + 3((1-t)^2)*t*P1 + 3(1-t)(t^2)P2 + (t^3)*P3
    0 = ((1-t)^3)*P0 + 3((1-t)^2)*t*P1 + 3(1-t)(t^2)P2 + (t^3)*P3 - y

    '''
    print('A,B,C,D:',A,',',B,',',C,',',D)

    coeff = [A,B,C,D-y]

    t_params = np.roots(coeff)

    for t in t_params:
        if t > 0 and t < 1:
            print('t :',t)
    # Plug t into x side of cubic bezier function to find B(t)_x
            x = (((1-t)**3)*bez[0][0]) + (bez[1][0]*(3*t - 6*t**2 + 3*t**3)) + ((3*t**2 - 3*t**3)*bez[2][0]) + ((t**3)*bez[3][0])

            return (x,y)



print(find_intersect(60,test_curve))


