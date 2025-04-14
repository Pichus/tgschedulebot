from attr import dataclass


@dataclass(eq=False)
class SubjectModel:
    text: str
    row: int
    col: int

    def __eq__(self, other):
        if not isinstance(other, SubjectModel):
            return NotImplemented

        return self.text == other.text
