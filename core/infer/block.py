class Block:
    def __init__(self, content, block_type="event"):
        self.content = content
        self.block_type = block_type

    def __repr__(self):
        return f"<Block type={self.block_type} content={self.content}>"
