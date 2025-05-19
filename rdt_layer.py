from segment import Segment


class RDTLayer(object):
    DATA_LENGTH = 4  # in characters
    FLOW_CONTROL_WIN_SIZE = 15  # in characters
    TIMEOUT = 5  # iterations before retransmission
    
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0
    
    # Sender state
    next_seqnum = 0  # next sequence number to use
    base_seqnum = 0  # oldest unacked sequence number
    send_buffer = []  # buffer of unacked segments
    last_ack_received = -1  # last ack number received
    
    # Receiver state
    expected_seqnum = 0  # next expected sequence number
    receive_buffer = {}  # buffer for out-of-order segments
    received_data = ""  # accumulated received data
    
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        
        # Initialize sender state
        self.next_seqnum = 0
        self.base_seqnum = 0
        self.send_buffer = []
        self.last_ack_received = -1
        
        # Initialize receiver state
        self.expected_seqnum = 0
        self.receive_buffer = {}
        self.received_data = ""
        
        # Statistics
        self.countSegmentTimeouts = 0

    def setSendChannel(self, channel):
        self.sendChannel = channel

    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    def setDataToSend(self, data):
        self.dataToSend = data

    def getDataReceived(self):
        return self.received_data

    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    def processSend(self):
        # Check for timeouts
        for seg in self.send_buffer:
            if self.currentIteration - seg.getStartIteration() > self.TIMEOUT:
                print(f"Timeout detected for segment {seg.seqnum}")
                self.countSegmentTimeouts += 1
                self.base_seqnum = int(seg.seqnum)
                self.next_seqnum = self.base_seqnum
                break
        
        # Clear acknowledged segments from buffer
        self.send_buffer = [seg for seg in self.send_buffer 
                          if int(seg.seqnum) >= self.base_seqnum]
        
        # Send new segments that fit in the window
        window_size = min(self.FLOW_CONTROL_WIN_SIZE // self.DATA_LENGTH, 
                         len(self.dataToSend) // self.DATA_LENGTH + 1)
        
        while (self.next_seqnum < len(self.dataToSend) and 
               self.next_seqnum < self.base_seqnum + window_size * self.DATA_LENGTH):
            
            end_idx = min(self.next_seqnum + self.DATA_LENGTH, len(self.dataToSend))
            data = self.dataToSend[self.next_seqnum:end_idx]
            
            segmentSend = Segment()
            segmentSend.setData(str(self.next_seqnum), data)
            segmentSend.setStartIteration(self.currentIteration)
            
            print(f"Sending segment: {segmentSend.to_string()}")
            self.sendChannel.send(segmentSend)
            
            self.send_buffer.append(segmentSend)
            self.next_seqnum += len(data)

    def processReceiveAndSendRespond(self):
        listIncomingSegments = self.receiveChannel.receive()
        segmentAck = Segment()
        max_ack = -1
        
        for seg in listIncomingSegments:
            if seg.acknum != -1:  # This is an ACK segment
                ack_num = int(seg.acknum)
                if ack_num > self.last_ack_received:
                    self.last_ack_received = ack_num
                    self.base_seqnum = ack_num + 1
            else:  # This is a data segment
                if not seg.checkChecksum():
                    print(f"Checksum failed for segment {seg.seqnum}")
                    continue
                    
                seq_num = int(seg.seqnum)
                if seq_num == self.expected_seqnum:
                    # Deliver in-order data
                    self.received_data += seg.payload
                    self.expected_seqnum += len(seg.payload)
                    
                    # Check if we can deliver any buffered packets
                    while self.expected_seqnum in self.receive_buffer:
                        self.received_data += self.receive_buffer[self.expected_seqnum]
                        del self.receive_buffer[self.expected_seqnum]
                        self.expected_seqnum += len(self.receive_buffer.get(self.expected_seqnum, ''))
                    
                    max_ack = self.expected_seqnum - 1
                elif seq_num > self.expected_seqnum:
                    # Buffer out-of-order data
                    self.receive_buffer[seq_num] = seg.payload
                    max_ack = self.expected_seqnum - 1
                else:
                    # Duplicate packet, acknowledge anyway
                    max_ack = max(max_ack, seq_num + len(seg.payload) - 1)
        
        # Send cumulative ACK
        if max_ack != -1:
            segmentAck.setAck(str(max_ack))
            print(f"Sending ack: {segmentAck.to_string()}")
            self.sendChannel.send(segmentAck)