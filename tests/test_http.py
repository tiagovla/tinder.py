from tinder import http


def test_route_get_method():
    r_get = http.Route("GET", "/test")
    assert r_get.method == "GET"
    assert r_get.url == "https://api.gotinder.com/test"


def test_route_post_method():
    r_post = http.Route("POST", "/test")
    assert r_post.method == "POST"
    assert r_post.url == "https://api.gotinder.com/test"


def test_route_format():
    r = http.Route("GET", "/test/{test}", test="working")
    assert r.method == "GET"
    assert r.url == "https://api.gotinder.com/test/working"
