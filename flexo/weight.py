import parsley


class WeightMixin(object):
    weight_expr = None
    metric_group = None
    _weight_expr = None

    def __init__(self, *args, **kwargs):
        weight_expr = None
        if 'weight' in kwargs:
            weight_expr = kwargs['weight']
            del kwargs['weight']
        super(WeightMixin, self).__init__(*args, **kwargs)
        if weight_expr:
            self.weight = weight_expr

    def find_metric_group(self):
        node = self
        while node:
            if hasattr(node, 'metric_group') and node.metric_group:
                return node.metric_group
            node = node._instance if hasattr(node, '_instance') else None
        return None

    @property
    def weight(self):
        self.metric_group = self.find_metric_group()
        self._weight_expr = WeightExpr(self.weight_expr, self.metric_group)
        return self._weight_expr.eval()

    @weight.setter
    def weight(self, value):
        self.weight_expr = str(value)


class WeightExpr(object):
    """
    An expression representing a weight.

    All weights are returned in kg. Any tokens specified as lb are converted to kg.

    e.g.
    80
    100kg
    200lb
    70% of 1RM
    80% of 5RM + 5kg
    (1RM + 5kg) * 80%
    (5+1)/8+7
    1RM + 50lb
    """

    grammar = """
    float = <digit+ '.' digit+>:ds -> float(ds)
    integer = <digit+>:ds -> int(ds)
    parens = '(' ws expr:e ws ')' -> e
    number = float | integer
    percent = number:n '%' -> float(n)/100
    repmax = number:n ('rm' | 'RM') -> repmax(n)
    pounds = number:n ('lb' | 'LB' | '#') -> lb2kg(n)
    kilograms = number:n ('kg' | 'KG') -> n
    weight = pounds | kilograms
    value = weight | percent | repmax | number | parens
    ws = ' '*
    add = '+' ws expr2:n -> ('+', n)
    sub = '-' ws expr2:n -> ('-', n)
    mul = '*' ws value:n -> ('*', n)
    of = 'of' ws value:n -> ('*', n)
    div = '/' ws value:n -> ('/', n)

    addsub = ws (add | sub)
    muldiv = ws (mul | div | of)

    expr = expr2:left addsub*:right -> calculate(left, right)
    expr2 = value:left muldiv*:right -> calculate(left, right)
    """
    resolution = None

    def __init__(self, expr, metric_group=None, resolution=0.5):
        def calculate(start, pairs):
            result = start
            for op, value in pairs:
                if op == '+':
                    result += value
                elif op == '-':
                    result -= value
                elif op == '*':
                    result *= value
                elif op == '/':
                    result /= value
            return result

        def repmax(reps):
            return self.metric_group[reps].weight

        self.expr = expr
        self.metric_group = metric_group
        self.resolution = resolution

        self.parser = parsley.makeGrammar(
            WeightExpr.grammar,
            {"calculate": calculate, 'repmax': repmax, 'lb2kg': lambda n: n * 0.45359237})

    def __repr__(self):
        return str(self.eval())

    def __int__(self):
        return int(self.eval())

    def __float__(self):
        return float(self.eval())

    def __abs__(self):
        return abs(float(self.eval()))

    def __add__(self, value):
        return float(self.eval()) + value

    def __radd__(self, value):
        return float(self.eval()) + value

    def __and__(self, value):
        return float(self.eval()) & value

    def __mul__(self, value):
        return float(self) * value

    def __rmul__(self, value):
        return float(self) * value

    def __div__(self, value):
        return float(self.eval()) / value

    def __rdiv__(self, value):
        return float(self.eval()) / value

    def __floordiv__(self, value):
        return float(self.eval()) // value

    def __index__(self):
        return int(self.eval())

    def __mod__(self, value):
        return float(self.eval()) % value

    def __rmod__(self, value):
        return float(self.eval()) % value

    def __neg__(self):
        return -float(self.eval())

    def __pos__(self):
        return +float(self.eval())

    def __pow__(self, value):
        return float(self.eval()) ** value

    def __sub__(self, value):
        return float(self.eval()) - value

    def __rsub__(self, value):
        return float(self.eval()) - value

    def __eq__(self, value):
        return float(self) == value

    def __ne__(self, value):
        return float(self) != value

    def __lt__(self, value):
        return float(self) < value

    def __le__(self, value):
        return float(self) <= value

    def __gt__(self, value):
        return float(self) > value

    def __ge__(self, value):
        return float(self) >= value

    @property
    def expr(self):
        return self._expr

    @expr.setter
    def expr(self, value):
        self._expr = str(value)

    def eval(self):
        res = self.round(self.parser(self.expr).expr(), self.resolution)
        return res

    def round(self, value, resolution):
        if resolution == 0:
            return 0
        elif resolution is None:
            return value
        return round(value / resolution) * resolution
