class _ErrorFactory(Exception):
	def __init__(self, name:str, reason:str, *args):
		self.name = name
		self.reason = reason

	def __str__(self):
		return f"<Koishi {self.name} error, {self.reason}>"
	def __repr__(self):
		return str(self)


class LoginError(_ErrorFactory):
	def __init__(self, reason:str, *args):
		super().__init__("Login", reason, *args)

class AccessError(_ErrorFactory):
	def __init__(self, reason:str, *args):
		super().__init__("Permission", reason, *args)