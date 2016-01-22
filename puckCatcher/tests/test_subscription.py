import nose.tools as NT

import puckCatcher.subscription as SUB
import puckCatcher.puckError as PE

rssTestHost = "https://www.andrewmichaud.com/"
rssAddress = rssTestHost + "rss.xml"
rssResourceAddress = rssTestHost + "hi.txt"
http302Address = rssTestHost + "302rss.xml"
http301Address = rssTestHost + "301rss.xml"
http404Address = rssTestHost + "404rss.xml"
http410Address = rssTestHost + "410rss.xml"


def test_emptyUrlConstructionErrors():
    """
    Constructing a subscription with a URL that is empty should throw a MalformedSubscriptionError.
    """
    with NT.assert_raises(PE.MalformedSubscriptionError) as e:
        SUB.Subscription(url="", name="emptyConstruction")

    NT.assert_equal(e.exception.desc, "No URL provided.")


def test_noneUrlConstructionErrors():
    """
    Constructing a subscription with a URL that is None should throw a MalformedSubscriptionError.
    """
    with NT.assert_raises(PE.MalformedSubscriptionError) as e:
        SUB.Subscription(name="noneConstruction")

    NT.assert_equal(e.exception.desc, "No URL provided.")


def test_emptyDaysConstructedCorrectly():
    """
    A subscription constructed with an empty days list should have an array
    of all false for its days list.
    """
    emptySubscription = SUB.Subscription(url=rssAddress)
    NT.assert_equal(emptySubscription.days, [False]*7)


def test_numberDaysConstructedCorrectly():
    """
    A subscription initialized with day numbers should parse them correctly.
    Invalid days should be silently ignored.
    """
    sub = SUB.Subscription(name="numberDaysTest", url=rssAddress, days=[1, 2, 42, 5, 7, 0, 0, 1, 2])
    NT.assert_equal(sub.days, [True, True, False, False, True, False, True])


def test_stringDaysConstructedCorrectly():
    """
    A subscription initialized with day strings should parse them correctly.
    Invalid strings should be silently ignored.
    """
    sub = SUB.Subscription(name="stringDaysTest",
                           url=rssAddress,
                           days=[ "Monday"
                                , "Tuesday"
                                , "Wed"
                                , "Fish"
                                , "Friiiiiiiiiiiday"
                                , "Sunblargl"])
    NT.assert_equal(sub.days, [True, True, True, False, True, False, True])


def test_mixedDaysParsedCorrectly():
    """
    A mixture of string and int days should be parsed correctly.
    Invalid elements should be silently ignored.
    """
    sub = SUB.Subscription(name="mixedDaysTest",
                           url=rssAddress,
                           days=[ "Monday"
                                , 2
                                , "Wed"
                                , "Fish"
                                , 42
                                , "Friiiiiiiiiiiday"
                                , "Sunblargl"])
    NT.assert_equal(sub.days, [True, True, True, False, True, False, True])


def test_emptyURLAfterConstructionFails():
    """If we set the URL to empty after construction, getting latest entry should fail."""
    sub = SUB.Subscription(url=http302Address, name="emptyTest")
    sub.currentUrl = ""
    with NT.assert_raises(PE.MalformedSubscriptionError) as e:
        sub.getEntry(0)

    NT.assert_equal(e.exception.desc, "No URL after construction of subscription.")


def test_noneURLAfterConstructionFails():
    """If we set the URL to None after construction, getting latest entry should fail."""
    sub = SUB.Subscription(url=http302Address, name="noneTest")
    sub.currentUrl = None
    with NT.assert_raises(PE.MalformedSubscriptionError) as e:
        sub.getEntry(0)

    NT.assert_equal(e.exception.desc, "No URL after construction of subscription.")


def test_getEntryHelperFailsAfterMax():
    """If we try more than MAX_RECURSIVE_ATTEMPTS to retrieve a URL, we should fail."""
    sub = SUB.Subscription(url=http302Address, name="tooManyAttemptsTest")
    with NT.assert_raises(PE.UnreachableFeedError) as e:
        sub.getEntryHelper(entryAge=0, attemptCount=SUB.MAX_RECURSIVE_ATTEMPTS+1)

    NT.assert_equal(e.exception.desc, "Too many attempts needed to reach feed.")


def test_validTemporaryRedirectSucceeds():
    """
    If we are redirected temporarily to a valid RSS feed, we should successfully parse that feed
    and not change our url. The originally provided URL should be unchanged.
    """

    sub = SUB.Subscription(url=http302Address, name="302Test")
    NT.assert_equal(sub.getEntry(0)["link"], rssResourceAddress)
    NT.assert_equal(sub.currentUrl, http302Address)
    NT.assert_equal(sub.providedUrl, http302Address)


def test_validPermanentRedirectSucceeds():
    """
    If we are redirected permanently to a valid RSS feed, we should successfully parse that feed
    and change our url.  The originally provided URL should be unchanged
    """

    sub = SUB.Subscription(url=http301Address, name="301Test")
    NT.assert_equal(sub.getEntry(0)["link"], rssResourceAddress)
    NT.assert_equal(sub.currentUrl, rssAddress)
    NT.assert_equal(sub.providedUrl, http301Address)


def test_notFoundFails():
    """
    If the URL is Not Found, we should not change the saved URL, but we should return None.
    """

    with NT.assert_raises(PE.UnreachableFeedError) as e:
        sub = SUB.Subscription(url=http404Address, name="404Test")
        NT.assert_equal(sub.getEntry(entryAge=0), None)
        NT.assert_equal(sub.currentUrl, http404Address)
        NT.assert_equal(sub.providedUrl, http404Address)

    NT.assert_equal(e.exception.desc, "Unable to retrieve podcast.")


def test_goneFails():
    """
    If the URL is Gone, the currentUrl should be set to None, and we should return None.
    """

    with NT.assert_raises(PE.UnreachableFeedError) as e:
        sub = SUB.Subscription(url=http410Address, name="410Test")
        NT.assert_equal(sub.getEntry(entryAge=0), None)
        NT.assert_equal(sub.currentUrl, None)
        NT.assert_equal(sub.providedUrl, http410Address)

    NT.assert_equal(e.exception.desc, "Unable to retrieve podcast.")
