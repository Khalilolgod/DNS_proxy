def decode_name(data, offset):
    labels = []
    original_offset = offset
    jumped = False

    while True:
        label_len = data[offset]
        if label_len == 0:
            break

        offset += 1
        if (label_len & 0xc0) == 0xc0:
            pointer_offset = int.from_bytes(
                data[offset-1:offset+1], 'big') & 0x3fff
            if not jumped:
                original_offset = offset + 1
                jumped = True
            offset = pointer_offset
            continue

        label = data[offset:offset + label_len]
        try:
            labels.append(label.decode('utf-8'))
        except UnicodeDecodeError:
            labels.append(idna.decode(label).decode('utf-8'))
        offset += label_len

    if jumped:
        return ".".join(labels), original_offset
    else:
        return ".".join(labels), offset + 1


def parse_dns_packet(packet):
    # Header section
    transaction_id = int.from_bytes(packet[:2], 'big')
    flags = int.from_bytes(packet[2:4], 'big')
    qdcount = int.from_bytes(packet[4:6], 'big')
    ancount = int.from_bytes(packet[6:8], 'big')
    nscount = int.from_bytes(packet[8:10], 'big')
    arcount = int.from_bytes(packet[10:12], 'big')
    offset = 12

    print("Header:")
    print(f"Transaction ID: {transaction_id}")
    print(f"Flags: {flags}")
    print(f"Questions: {qdcount}")
    print(f"Answers: {ancount}")
    print(f"Authority: {nscount}")
    print(f"Additional: {arcount}")

    # Question section
    print("\nQuestions:")
    for _ in range(qdcount):
        qname, offset = decode_name(packet, offset)
        qtype = int.from_bytes(packet[offset:offset + 2], 'big')
        qclass = int.from_bytes(packet[offset + 2:offset + 4], 'big')
        offset += 4
        print(f"Name: {qname}, Type: {qtype}, Class: {qclass}")

    # Resource Record sections
    sections = [("Answers", ancount), ("Authority",
                                       nscount), ("Additional", arcount)]
    for section_name, count in sections:
        print(f"\n{section_name}:")
        for _ in range(count):
            name, offset = decode_name(packet, offset)
            rtype = int.from_bytes(packet[offset:offset + 2], 'big')
            rclass = int.from_bytes(packet[offset + 2:offset + 4], 'big')
            ttl = int.from_bytes(packet[offset + 4:offset + 8], 'big')
            rdlength = int.from_bytes(packet[offset + 8:offset + 10], 'big')
            rdata = packet[offset + 10:offset + 10 + rdlength]
            ip = ''
            for hex in rdata:
                ip += str(hex) + '.'
            ip = ip[:-1]
            offset += 10 + rdlength
            print(
                f"Name: {name}, Type: {rtype}, Class: {rclass}, TTL: {ttl}, Data: {ip}")
