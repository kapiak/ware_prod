from django import dispatch

stock_increased = dispatch.Signal()
allocated_stock = dispatch.Signal()
