# fabstack

---

### Usage

fab -f kafka.py --set inc=service/kafka-coupon.json install:coupon
fab -f kafka.py --set inc=service/kafka-coupon.json config:coupon
fab -f kafka.py --set inc=service/kafka-coupon.json start:coupon


fab -f kafka-pusher.py --set inc=service/kafka-coupon.json install:coupon
fab -f kafka-pusher.py --set inc=service/kafka-coupon.json config:coupon
fab -f kafka-pusher.py --set inc=service/kafka-coupon.json start:coupon


fab -f kafka-proxy.py --set inc=service/kafka-coupon.json install:coupon
fab -f kafka-proxy.py --set inc=service/kafka-coupon.json config:coupon
fab -f kafka-proxy.py --set inc=service/kafka-coupon.json start:coupon
