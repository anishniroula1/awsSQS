from FunctionCallTracer import trace_and_visualize_without_returns
from FunctionCallTracerWithReturns import trace_and_visualize_with_returns


def trace_and_visualize(func=None, include_stdlib=None, show_return: bool = True):
    if show_return:
        return trace_and_visualize_with_returns(func=func, include_stdlib=include_stdlib)
    else:
        return trace_and_visualize_without_returns(func=func, include_stdlib=include_stdlib)