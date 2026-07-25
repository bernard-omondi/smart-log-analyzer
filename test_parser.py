from parser import parse_line

def test_parse_valid():
    line = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
    result = parse_line(line)
    assert result['ip'] == '127.0.0.1'
    assert result['status'] == 200
    assert result['size'] == 2326

def test_parse_missing_size():
    line = '198.51.100.7 - jane [30/Jun/2024:18:30:22 +0200] "GET /report.pdf HTTP/1.1" 404 -'
    result = parse_line(line)
    assert result['size'] is None

def test_parse_garbage():
    assert parse_line("this is nonsense") is None

print("All tests pass!")