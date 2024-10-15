# notes for biomechzoo developers
Below is general guidance for biomechZoo developers

1. Try to maintain the "spirit" of the original Matlab code. This means, keeping similar folder 
   structures and function names
2. Move to object-oriented programming. This may mean coding new classes for biomechZoo operations
3. After creating a new feature (class/function/method), make sure to test it by adding code to the 
   ``tests`` folder. See test_c3d_reader.py for example implementation. To run tests, go to the terminal
   and type ``python -m unittest <TestClassName>.<methodName>``
4. Before making a pull request to the main branch, you should check that all tests work using
   ``python -m unittest discover -s tests`` 
