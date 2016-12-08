# image_boxing

Functions of keys:

  Before you use any key, you must click on the image first.

  When a window with cropped image is open:
  
    's' -> save this box and close window. Remembers a box and shows it in blue.
    
    any other key -> close window without saving this box
    
  Otherwise:
  
    'q', escape -> save csv file and quit
    
    'n', space, right arrow -> go to next picture
    
    'f' -> fast forward to next unboxed image. If there are no such images, does nothing.
    
    'c' -> clear all boxes on current image.
    
    'b', backspace, left arrow -> go back to previous picture.
    
Functions of mouse:

    left button down -> start drawing a rectangle. Color of a box that is currently being drawn is light green, color of already remembered is blue.
  
    right button down -> if currently drawing, ends it.
  
    left button up -> if currently drawing, ends it and shows a window with cropped image.
  
