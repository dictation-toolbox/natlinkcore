"""test_nsformat

Testing nsformat

  Quintijn Hoogenboom, Oct 2023
""" 
#pylint:disable=C0115, C0116
#pylint:disable=E1101
import pytest
from natlinkcore import nsformat


def test_formatWords():
    Input = "hello there".split()
    assert(nsformat.formatWords(Input)) == ("Hello there", set())

    Input = ["Sentence", "end",  r".\period\period", "next", r".\period\period"]
    result_text, state = nsformat.formatWords(Input)
    assert result_text == "Sentence end.  Next."
    assert state == {9, 4}
    
    Next = ["continue"]
    result_text, new_state = nsformat.formatWords(Next, state=state)
    assert result_text == "  Continue"
    assert new_state == set()
    
    sentence = "this is wrong."
    with pytest.raises(AssertionError):
        nsformat.formatWords(sentence)


def test_formatString():
    
    sentence = 'hello world. this is a test.'
    result, state = nsformat.formatString(sentence)
    assert result == "Hello world.  This is a test."
    assert state == {9, 4}
    total = [result]

    sentence = 'continue with?     what the fuck!'
    result, state = nsformat.formatString(sentence, state=state)
    assert result == "  Continue with?  What the fuck!"
    assert state == {9, 4}
    total.append(result)

    sentence = 'continue'
    result, state = nsformat.formatString(sentence, state=state)
    total.append(result)
    
    sentence = 'normal'
    result, state = nsformat.formatString(sentence, state=state)
    total.append(result)
    total_string = ''.join(total)    


    sentence = ', just normal'
    result, state = nsformat.formatString(sentence, state=state)
    total.append(result)
    total_string = ''.join(total)    

    assert total_string == "Hello world.  This is a test.  Continue with?  What the fuck!  Continue normal, just normal"
    assert state == set()
    
    # new example:
    sentence = 'hello again: this is a test- even if "quoted words" are not dealt with!'
    result, state = nsformat.formatString(sentence)
    assert result == 'Hello again: this is a test-even if "quoted words" are not dealt with!'
    assert state == {9, 4}
    total = [result]
    
    
    
# import sys
if __name__ == "__main__":
    pytest.main(['test_nsformat.py'])
    