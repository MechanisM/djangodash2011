staste - slightly complicated metrics for your django website
=============================================================

Say you want to count your guests. Also you want to aggregate them by genders and ages,and, of course, get a timeline.

You define two axes:

    gender_axis = Axis(choices=['boy', 'girl'])
    age_axis = StoredChoiceAxis()

(`StoredChoice` means that you won't give it all choices in advance)

And a Metrica:

    guests_metrica = Metrica(name='guest_visits_gender_age',
                             axes=[('gender', gender_axis),
                                   ('age', age_axis)])

And every time someone comes to your house, you call method `.kick` on your Metrica:

    guests_metrica.kick(date=prev_month,
                        gender='girl',
                        age=18)

Okay, fine. Now you can have some stats, like this:


    >>> metrica.timespan(year=2010).total()
    37

    >>> metrica.filter(gender='girl').total()
    8

    >>> metrica.filter(gender='girl', age=19).total()
    3

    >>> metrica.filter(gender='boy').timespan(year=2010, month=2).filter(age=17).total()
    10

    >>> metrica.timespan(year=2010, month=2).filter(gender='boy').iterate('age')
    [('120', 1), ('19', 0), ('17', 10), ('18', 17)]
    