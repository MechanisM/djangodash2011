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

    guests_metrica.kick(gender='girl',
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


It's all in Redis. So it's fast and you're the coolest kid in the block.

## Weighed and averaged metric

You don't always want to just count simple events. You can try counting more complicated things, like sums and averages.

To give event a weight, just provide a `value` keyword argument. Let's say you want to count your pocket money expenses:

    my_pocket_money_metric.kick(value=100, ...)

Everything is the same: you can use Axes, et cetera.

If you want to calculate averages, you'll need an AveragedMetrica class instead of Metrica. It will count both sum and quantity of your events:


    metrica = AveragedMetrica(name='some_averaged_metrica', axes=[('c', axis)], multiplier=100)

    d1 = datetime.datetime(2010, 2, 7)
    d2 = datetime.datetime(2010, 2, 8)
    d3 = datetime.datetime(2010, 2, 9)
    
    metrica.kick(date=d1, value=12, c='a')
    metrica.kick(date=d1, value=2, c='b')
    metrica.kick(date=d2, value=7.5, c='a')
    metrica.kick(date=d2, value=0.16, c='a')
    metrica.kick(date=d3, c='b')

    days = list(metrica.timespan(year=2010, month=2).iterate_counts())[5:10]
    self.assertEquals(days, [(6, 0), (7, 2), (8, 2), (9, 1), (10, 0)])

    days = list(metrica.timespan(year=2010, month=2).iterate_averages())[5:10]
    self.assertEquals(days, [(6, None), (7, 7), (8, 3.83), (9, 1), (10, None)])

    chars = list(metrica.filter().iterate_counts('c'))
    self.assertEquals(chars, [('a', 3), ('b', 2)])

    chars = list(metrica.filter().iterate_averages('c'))
    self.assertEquals(chars, [('a', (12+7.5+0.16)/3), ('b', 1.5)])

    