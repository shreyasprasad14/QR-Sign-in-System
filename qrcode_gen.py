import qrcode
import sys

def main():
    def print_usage():
        print("Usage:")
        print("python qrcode_gen.py <data>")
        print("python qrcode_gen.py -l <file>")
        
    if len(sys.argv) < 2:
        print_usage()
        return
    
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print_usage()
        return
    
    if sys.argv[1] == "-l" or sys.argv[1] == "--list":
        if len(sys.argv) != 3:
            print_usage()
            return
        
        with open(sys.argv[2], "r") as f:
            data = f.read()
            data = data.split("\n")
            for d in data:
                generate_qr_code(d)
        return


    data = ""
    
    for arg in sys.argv[1:]:
        data += arg + " "
    data = data.strip()

    generate_qr_code(data)

def generate_qr_code(data: str) -> None:
    img = qrcode.make(
        data,
        version=1,
    )

    img.save(f"img/{data}.png")

if __name__ == "__main__":
    main()