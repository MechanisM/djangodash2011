Staste - slightly complicated event tracker for your Django website
===================================================================

    pip install staste

## Quick Start

Say you want to track some event in *real time*, for example count your guests. And you want to count not only all of them, but have different counts by gender and age, and their combinations. Oh, and, of course, you don't want only static counts, you want a timeline.

You define two Axes and a Metrica:

    from staste.metrica import Metrica
    from staste.axis import Axis, StoredChoiceAxis
    
    gender_axis = Axis(choices=['boy', 'girl']) # preferable if you know all choices possible beforehand
    age_axis = StoredChoiceAxis() # this one accepts arbitrary values, but will store all of them in a Redis set

    guests_metrica = Metrica(name='guest_visits_gender_age',
                             axes=[('gender', gender_axis),
                                   ('age', age_axis)])

`Axis` is a parameter you'd like to filter your counts on. `Metrica` is an event tracker, collection of counters which you'll increment. So, we have this nice `guests_metrica` metrica for counting our guests.

Every time someone comes to your house, you call this very special method `.kick` on this very `Metrica` object:

    guests_metrica.kick(gender='girl', age=18)
    guests_metrica.kick(gender='boy', age=19)

That's it. From now on you'll have all necessary data.

## Warning

First of all, never, never ever change axes of your metricas. If you want to add or remove an axis, create a new metrica.

Keep in mind that every new axis in your metrica multiplies quantity of increments per kick by two. This is not going to be an issue for a reasonable amount of axes (2? 3? 5?), because Redis is fast. Oh, it's really fast. You'll never believe. It also does not use too much memory for such simple things like my counters.

## Getting stats

If you want stats in your code, getting them is simple:

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

## Nice charts

You have probably seen nice charts on the [Staste page][1]. Well, you can show them, using these very special generic views at `staste.charts.views`. Just add them to your urlconf like this:

    PieChart.as_view(metrica=gender_age_metrica,
                     axis_keyword='gender'),

Actually, these were made in hurry during the DjangoDash, 

## How does it work?

It has a lot of counters in Redis, and each time you kick a metrica, it bumps some of them. That simple.

Actually, not that simple. The algorithm uses `itertools.product()`. I've never used things like that for anything apart from puzzles (like ones at [Project Euler][2]).

## Battery included: request logging middleware!

Add 

    'staste.middleware.ResponseTimeMiddleware',

to your middleware classes. Counting requests and average time will start this very instant. They can be aggregated by the view function. [Example][1].

[1]: http://staste.unfoldthat.com/
[2]: http://projecteuler.net/