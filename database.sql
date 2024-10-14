-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: labsaledb2
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `brand`
--

DROP TABLE IF EXISTS `brand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brand` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brand`
--

LOCK TABLES `brand` WRITE;
/*!40000 ALTER TABLE `brand` DISABLE KEYS */;
INSERT INTO `brand` VALUES (1,'Apple'),(2,'Samsung'),(3,'Xiaomi'),(4,'MSI'),(5,'Acer'),(6,'Logictech');
/*!40000 ALTER TABLE `brand` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `parent_id` int DEFAULT NULL,
  `child` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (1,'Điện thoại',NULL,0),(2,'Tablet',NULL,0),(3,'Smartwatch',NULL,0),(4,'Loa',NULL,0),(5,'Laptop',NULL,0),(6,'Tai Nghe',11,0),(7,'Sạc, cáp',11,0),(8,'Chuột máy tính',11,0),(9,'Bàn phím',11,0),(10,'Ốp lưng',11,0),(11,'Phụ kiện',NULL,1);
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content` varchar(255) NOT NULL,
  `product_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`),
  CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comment`
--

LOCK TABLES `comment` WRITE;
/*!40000 ALTER TABLE `comment` DISABLE KEYS */;
INSERT INTO `comment` VALUES (3,'good',2,7,'2024-04-18 00:22:02'),(4,'good !!!\n',1,1,'2024-09-09 08:05:56');
/*!40000 ALTER TABLE `comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `delivery_reason`
--

DROP TABLE IF EXISTS `delivery_reason`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_reason` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(55) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_reason`
--

LOCK TABLES `delivery_reason` WRITE;
/*!40000 ALTER TABLE `delivery_reason` DISABLE KEYS */;
INSERT INTO `delivery_reason` VALUES (1,'Xuất bán'),(2,'Bảo trì sữa chữa '),(3,'Khuyến mãi tặng quà'),(4,'Bảo hành - đổi sản phẩm');
/*!40000 ALTER TABLE `delivery_reason` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distribution`
--

DROP TABLE IF EXISTS `distribution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `distribution` (
  `product_id` int NOT NULL,
  `provider_id` int NOT NULL,
  PRIMARY KEY (`product_id`,`provider_id`),
  KEY `provider_id` (`provider_id`),
  CONSTRAINT `distribution_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`),
  CONSTRAINT `distribution_ibfk_2` FOREIGN KEY (`provider_id`) REFERENCES `provider` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distribution`
--

LOCK TABLES `distribution` WRITE;
/*!40000 ALTER TABLE `distribution` DISABLE KEYS */;
INSERT INTO `distribution` VALUES (20,1),(25,1),(30,1),(34,1),(35,1),(37,1),(39,1),(42,1),(43,1),(46,1),(53,1),(57,1),(79,1),(83,1),(630867,1),(2,2),(4,2),(22,2),(24,2),(32,2),(40,2),(41,2),(48,2),(51,2),(55,2),(61,2),(64,2),(65,2),(67,2),(68,2),(70,2),(77,2),(78,2),(1,3),(3,3),(16,3),(27,3),(29,3),(44,3),(45,3),(52,3),(63,3),(73,3),(80,3),(630229,3),(17,4),(21,4),(26,4),(28,4),(31,4),(36,4),(58,4),(59,4),(23,5),(38,5),(47,5),(49,5),(54,5),(60,5),(62,5),(33,6),(50,6),(66,6),(69,6),(71,6),(72,6),(74,6),(75,6),(76,6),(81,6),(82,6);
/*!40000 ALTER TABLE `distribution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `district`
--

DROP TABLE IF EXISTS `district`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `district` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `district`
--

LOCK TABLES `district` WRITE;
/*!40000 ALTER TABLE `district` DISABLE KEYS */;
INSERT INTO `district` VALUES (1,'Quận 1'),(2,'Quận 3'),(3,'Quận 4'),(4,'Quận 5'),(5,'Quận 7'),(6,'Quận Bình Thạnh'),(7,'Quận Thủ Đức'),(8,'Quận Gò Vấp'),(9,'Quận 2'),(10,'Quận 6'),(11,'Quận 8'),(12,'Quận 9'),(13,'Quận 10'),(14,'Quận 11'),(15,'Quận 12'),(16,'Quận Bình Tân'),(17,'Quận Phú Nhuận'),(18,'Quận Tân Phú'),(19,'Quận Tân Bình');
/*!40000 ALTER TABLE `district` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goods_delivery_note`
--

DROP TABLE IF EXISTS `goods_delivery_note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goods_delivery_note` (
  `code` varchar(255) NOT NULL,
  `created_date` datetime NOT NULL,
  `reason` int NOT NULL,
  `user_created` int NOT NULL,
  `delivery_address` varchar(255) NOT NULL,
  `total_price` float NOT NULL,
  `confirmed` tinyint(1) NOT NULL,
  `confirm_date` datetime DEFAULT NULL,
  `delivery_man` int NOT NULL,
  `for_receipt_id` int DEFAULT NULL,
  PRIMARY KEY (`code`),
  KEY `user_created` (`user_created`),
  KEY `ix_goods_delivery_note_reason` (`reason`),
  KEY `ix_goods_delivery_note_delivery_man` (`delivery_man`),
  KEY `ix_goods_delivery_note_for_receipt_id` (`for_receipt_id`),
  KEY `ix_goods_delivery_note_created_date` (`created_date`),
  CONSTRAINT `goods_delivery_note_ibfk_1` FOREIGN KEY (`reason`) REFERENCES `delivery_reason` (`id`),
  CONSTRAINT `goods_delivery_note_ibfk_2` FOREIGN KEY (`user_created`) REFERENCES `user` (`id`),
  CONSTRAINT `goods_delivery_note_ibfk_3` FOREIGN KEY (`delivery_man`) REFERENCES `user` (`id`),
  CONSTRAINT `goods_delivery_note_ibfk_4` FOREIGN KEY (`for_receipt_id`) REFERENCES `receipt` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goods_delivery_note`
--

LOCK TABLES `goods_delivery_note` WRITE;
/*!40000 ALTER TABLE `goods_delivery_note` DISABLE KEYS */;
INSERT INTO `goods_delivery_note` VALUES ('DP044C2P','2024-09-27 04:27:11',1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',55960000,1,NULL,8,18),('DP047OEQ','2024-09-27 05:15:59',1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',80970000,1,NULL,8,19),('DP0486K7','2024-10-02 08:17:01',1,1,'629 KDV, phường An Lạc, quận Bình Tân, TPHCM',149533000,0,NULL,8,32),('DP04E0GP','2024-09-29 02:27:46',1,1,'C13/15D Cư Xá Phú Lâm B, phường 13, quận 6, TP Hồ Chí Minh',95564000,1,NULL,8,30),('DP04E9HB','2024-09-27 04:22:43',1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',62970000,1,'2024-09-27 04:50:03',8,23),('DP04GFNE','2024-09-27 04:27:48',1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',218190000,0,NULL,8,4),('DP04U9KJ','2024-10-02 08:17:33',1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',167920000,1,NULL,8,28),('DP04ZPCI','2024-10-07 14:39:40',1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',30583000,1,NULL,8,33);
/*!40000 ALTER TABLE `goods_delivery_note` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goods_delivery_note_detail`
--

DROP TABLE IF EXISTS `goods_delivery_note_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goods_delivery_note_detail` (
  `goods_delivery_note_code` varchar(255) NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `delivered_quantity` int DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`goods_delivery_note_code`,`product_id`),
  KEY `ix_goods_delivery_note_detail_goods_delivery_note_code` (`goods_delivery_note_code`),
  KEY `ix_goods_delivery_note_detail_product_id` (`product_id`),
  CONSTRAINT `goods_delivery_note_detail_ibfk_1` FOREIGN KEY (`goods_delivery_note_code`) REFERENCES `goods_delivery_note` (`code`),
  CONSTRAINT `goods_delivery_note_detail_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goods_delivery_note_detail`
--

LOCK TABLES `goods_delivery_note_detail` WRITE;
/*!40000 ALTER TABLE `goods_delivery_note_detail` DISABLE KEYS */;
INSERT INTO `goods_delivery_note_detail` VALUES ('DP044C2P',3,4,4,''),('DP047OEQ',17,3,3,''),('DP0486K7',1,1,1,''),('DP0486K7',2,1,1,''),('DP0486K7',24,2,1,''),('DP04E0GP',16,1,1,''),('DP04E0GP',24,2,2,''),('DP04E0GP',38,1,1,''),('DP04E9HB',24,3,3,''),('DP04GFNE',2,1,1,''),('DP04GFNE',4,1,1,''),('DP04GFNE',23,1,1,''),('DP04GFNE',25,1,1,''),('DP04GFNE',26,1,1,''),('DP04GFNE',39,1,1,''),('DP04GFNE',42,1,0,''),('DP04U9KJ',24,5,5,''),('DP04ZPCI',1,1,1,'');
/*!40000 ALTER TABLE `goods_delivery_note_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goods_received_note`
--

DROP TABLE IF EXISTS `goods_received_note`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goods_received_note` (
  `code` varchar(255) NOT NULL,
  `order_date` datetime NOT NULL,
  `provider_id` int NOT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `confirm_date` datetime DEFAULT NULL,
  `user_confirm` int DEFAULT NULL,
  `total_price` float DEFAULT NULL,
  `delivery_man` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`code`),
  KEY `provider_id` (`provider_id`),
  CONSTRAINT `goods_received_note_ibfk_1` FOREIGN KEY (`provider_id`) REFERENCES `provider` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goods_received_note`
--

LOCK TABLES `goods_received_note` WRITE;
/*!40000 ALTER TABLE `goods_received_note` DISABLE KEYS */;
INSERT INTO `goods_received_note` VALUES ('RP044XHQ','2024-09-22 15:17:38',3,1,'2024-09-24 02:07:07',1,390528000,'Thái Thạch'),('RP04F9PU','2024-09-24 00:28:47',3,1,'2024-10-02 08:18:12',1,283560000,'Tuan'),('RP04R9XJ','2024-09-24 00:34:40',1,1,'2024-10-07 23:52:38',1,139152000,'Thái Lan'),('RP04S8FG','2024-10-08 00:00:00',1,0,NULL,NULL,375120000,NULL),('RP04U4YW','2024-10-02 00:00:00',1,0,NULL,NULL,121552000,'Thái Thạch');
/*!40000 ALTER TABLE `goods_received_note` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goods_received_note_detail`
--

DROP TABLE IF EXISTS `goods_received_note_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goods_received_note_detail` (
  `goods_received_note_code` varchar(255) NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `received_quantity` int DEFAULT NULL,
  PRIMARY KEY (`goods_received_note_code`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `goods_received_note_detail_ibfk_1` FOREIGN KEY (`goods_received_note_code`) REFERENCES `goods_received_note` (`code`),
  CONSTRAINT `goods_received_note_detail_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goods_received_note_detail`
--

LOCK TABLES `goods_received_note_detail` WRITE;
/*!40000 ALTER TABLE `goods_received_note_detail` DISABLE KEYS */;
INSERT INTO `goods_received_note_detail` VALUES ('RP044XHQ',25,12,NULL,12),('RP044XHQ',26,12,NULL,12),('RP04F9PU',23,5,'',5),('RP04F9PU',39,5,NULL,3),('RP04R9XJ',33,2,'',2),('RP04R9XJ',40,4,'Nợ',3),('RP04S8FG',1,10,'',0),('RP04S8FG',23,10,'',0),('RP04U4YW',32,2,'',1),('RP04U4YW',33,2,'',1),('RP04U4YW',40,2,'',1);
/*!40000 ALTER TABLE `goods_received_note_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `logo` varchar(55) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,'Tiền mặt','fa-solid fa-money-bills'),(2,'Momo','building-columns'),(3,'Paypal','fa-brands fa-cc-paypal'),(4,'Visa','fa-brands fa-cc-visa');
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `privileged`
--

DROP TABLE IF EXISTS `privileged`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `privileged` (
  `user_id` int NOT NULL,
  `user_role` int NOT NULL,
  PRIMARY KEY (`user_id`,`user_role`),
  KEY `user_role` (`user_role`),
  CONSTRAINT `privileged_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `privileged_ibfk_2` FOREIGN KEY (`user_role`) REFERENCES `user_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `privileged`
--

LOCK TABLES `privileged` WRITE;
/*!40000 ALTER TABLE `privileged` DISABLE KEYS */;
INSERT INTO `privileged` VALUES (1,1),(7,2),(8,3),(9,4),(10,5);
/*!40000 ALTER TABLE `privileged` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `price` float DEFAULT NULL,
  `image` varchar(100) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `category_id` int NOT NULL,
  `brand_id` int NOT NULL,
  `import_price` float DEFAULT NULL,
  `rating` varchar(45) DEFAULT NULL,
  `warranty` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `product_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=630868 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES (1,'IPhone 7 Plus','Màn hình:  LED-backlit IPS LCD5.5\"Retina HD Hệ điều hành:  iOS 14 Camera sau:  2 camera 12 MP Camera trước:  7 MP Chip:  Apple A10 Fusion RAM:  3 GB Dung lượng lưu trữ:  256 GB SIM:  1 Nano SIM Pin, Sạc:  2900 mAh Hãng  iPhone (Apple)',17990000,'images/iphone7.jpg',1,'2024-04-09 18:16:05',1,0,14392000,NULL,1),(2,'IPad Pro 2020','Màn hình:  12.9\"Liquid Retina Hệ điều hành:  iPadOS 15 Chip:  Apple A12Z Bionic RAM:  6 GB Dung lượng lưu trữ:  128 GB Kết nối:  Nghe gọi qua FaceTime Camera sau:  Chính 12 MP & Phụ 10 MP, TOF 3D LiDAR Camera trước:  7 MP Pin, Sạc:  36.71 Wh (~ 9720 mAh)1',36990000,'images/ipadpro20.jpg',1,'2024-04-09 18:16:05',2,0,29592000,NULL,1),(3,'IPhone 6 Plus','Màn hình:  LED-backlit IPS LCD5.5\"Retina HD Hệ điều hành:  iOS 10 Camera sau:  8 MP Camera trước:  1.2 MP Chip:  Apple A8 RAM:  1 GB Dung lượng lưu trữ:  32 GB SIM:  1 Nano SIM Pin, Sạc:  2915 mAh Hãng  iPhone (Apple)',13990000,'images/iphone6.jpg',1,'2024-04-09 18:16:05',1,0,11192000,NULL,1),(4,'IPad Mini 2020','Màn hình: 8.3\"Liquid Retina Hệ điều hành: iPadOS 15 Chip: Apple A12Z Bionic RAM: 6 GB Dung lượng lưu trữ: 128 GB Kết nối: Nghe gọi qua FaceTime Camera sau: Chính 12 MP & Phụ 10 MP, TOF 3D LiDAR Camera trước: 7 MP Pin, Sạc: 36.71 Wh (~ 9720 mAh)1',29000000,'images/ipadmini.jpg',1,'2024-04-09 18:16:05',2,0,23200000,NULL,1),(16,'Iphone 8','Màn hình:  LED-backlit IPS LCD4.7\"Retina HD Hệ điều hành:  iOS 14 Camera sau:  12 MP Camera trước:  7 MP Chip:  Apple A11 Bionic RAM:  2 GB Dung lượng lưu trữ:  64 GB SIM:  1 Nano SIM Pin, Sạc:  1821 mAh Hãng  iPhone (Apple)',22990000,'images/iphone8.jpg',1,'2024-04-15 19:19:00',1,0,18392000,NULL,1),(17,'Iphone X','Màn hình:  OLED5.8\"Super Retina Hệ điều hành:  iOS 12 Camera sau:  2 camera 12 MP Camera trước:  7 MP Chip:  Apple A11 Bionic RAM:  3 GB Dung lượng lưu trữ:  256 GB SIM:  1 Nano SIM Pin, Sạc:  2716 mAh Hãng  iPhone (Apple)',26990000,'images/iphoneX.jpg',1,'2024-04-15 19:19:00',1,0,21592000,NULL,1),(20,'AirPods2','Thời gian tai nghe:  Dùng 6 giờ Thời gian hộp sạc:  Dùng 30 giờ Cổng sạc:  Sạc MagSafeSạc không dây QiLightning Công nghệ âm thanh:  Chip Apple H2Adaptive EQActive Noise Cancellation Tương thích:  macOS (Macbook, iMac)Android, iOS, Windows Tiện ích:  Trợ ',6190000,'images/airpods2.jpg',1,'2024-04-15 19:19:00',6,0,4952000,'0',1),(21,'OPENFIT T910','Thời gian tai nghe:  Dùng 7 giờ - Sạc 1 giờ Thời gian hộp sạc:  Dùng 28 giờ - Sạc 2 giờ Cổng sạc:  Type-C Công nghệ âm thanh:  Dẫn truyền khí DirectPitch Tương thích:  macOSAndroid, iOS, Windows Tiện ích:  Sạc nhanhKhử tiếng ồn AIChống nước & bụi IP542 Mi',5690000,'images/openfitt910.jpg',1,'2024-04-15 19:19:00',6,0,4552000,NULL,1),(22,'Iphone 13','Màn hình:  OLED6.1\"Super Retina XDR Hệ điều hành:  iOS 15 Camera sau:  2 camera 12 MP Camera trước:  12 MP Chip:  Apple A15 Bionic RAM:  4 GB Dung lượng lưu trữ:  256 GB SIM:  1 Nano SIM & 1 eSIMHỗ trợ 5G Pin, Sạc:  3240 mAh20 W Hãng  iPhone (Apple)',38900000,'images/iphone13.jpg',1,'2024-04-15 20:36:10',1,0,31120000,NULL,1),(23,'Xiaomi 13T Pro 5G ','Màn hình:  AMOLED6.67\"1.5K Hệ điều hành:  Android 13 Camera sau:  Chính 50 MP & Phụ 50 MP, 12 MP Camera trước:  20 MP Chip:  MediaTek Dimensity 9200+ 5G 8 nhân RAM:  12 GB Dung lượng lưu trữ:  256 GB SIM:  2 Nano SIMHỗ trợ 5G Pin, Sạc:  5000 mAh120 W Hãng',28900000,'images/xiaomi13tpro.jpg',1,'2024-04-15 20:36:10',1,0,23120000,NULL,1),(24,'Samsung Galxy A54','Màn hình:  Super AMOLED6.4\"Full HD+ Hệ điều hành:  Android 13 Camera sau:  Chính 50 MP & Phụ 12 MP, 5 MP Camera trước:  32 MP Chip:  Exynos 1380 8 nhân RAM:  8 GB Dung lượng lưu trữ:  128 GB SIM:  2 Nano SIMHỗ trợ 5G Pin, Sạc:  5000 mAh25 W Hãng  Samsung',20990000,'images/ssgalaxya54.jpg',1,'2024-04-15 20:36:10',1,0,16792000,NULL,1),(25,'Ipad Air 5 M1 Wifi','Màn hình:  10.9\"Retina IPS LCD Hệ điều hành:  iPadOS 15 Chip:  Apple M1 RAM:  8 GB Dung lượng lưu trữ:  64 GB Kết nối:  Nghe gọi qua FaceTime Camera sau:  12 MP Camera trước:  12 MP Pin, Sạc:  28.6 Wh (~ 7587 mAh)20 W Hãng  iPad (Apple)',25690000,'images/ipadair5m1.jpg',1,'2024-04-15 20:36:10',2,0,20552000,NULL,1),(26,'Ipad 9 Wifi','Màn hình:  10.2\"Retina IPS LCD Hệ điều hành:  iPadOS 15 Chip:  Apple A13 Bionic RAM:  3 GB Dung lượng lưu trữ:  256 GB Kết nối:  Nghe gọi qua FaceTime Camera sau:  8 MP Camera trước:  12 MP Pin, Sạc:  32.4 Wh (~ 8600 mAh)20 W Hãng  iPad (Apple)',14990000,'images/ipad9.jpg',1,'2024-04-15 20:36:10',2,0,11992000,NULL,1),(27,'Ipad Pro M2 12.9 inch Wifi','Màn hình:  12.9\"Liquid Retina XDR Hệ điều hành:  iPadOS 16 Chip:  Apple M2 8 nhân RAM:  8 GB Dung lượng lưu trữ:  256 GB Kết nối:  Nghe gọi qua FaceTime Camera sau:  Chính 12 MP & Phụ 10 MP, TOF 3D LiDAR Camera trước:  12 MP Pin, Sạc:  40.88 Wh (~ 10.835 ',32990000,'images/ipadprom2.jpg',1,'2024-04-15 20:36:10',2,0,26392000,NULL,1),(28,'Macbook Air 13 Inch M3','CPU:  Apple M3100GB/s RAM:  16 GB Ổ cứng:  512 GB SSD Màn hình:  13.6\"Liquid Retina (2560 x 1664) Card màn hình:  Card tích hợp10 nhân GPU Cổng kết nối:  MagSafe 3Jack tai nghe 3.5 mm2 x Thunderbolt 3 / USB 4 (lên đến 40 Gb/s) Đặc biệt:  Có đèn bàn phím H',42990000,'images/macbookair13m3.jpg',1,'2024-04-15 20:36:10',5,0,34392000,NULL,1),(29,'Macbook Air 15 Inch M2','CPU:  Apple M2100GB/s RAM:  16 GB Ổ cứng:  256 GB SSD Màn hình:  15.3\"Liquid Retina (2880 x 1864) Card màn hình:  Card tích hợp10 nhân GPU Cổng kết nối:  MagSafe 3Jack tai nghe 3.5 mm2 x Thunderbolt / USB 4 (hỗ trợ DisplayPort, Thunderbolt 3 (up to 40Gb/s',44990000,'images/macbookair15m2.jpg',1,'2024-04-15 20:36:10',5,0,35992000,NULL,1),(30,'Apple Watch Series 9 GPS','Màn hình:  OLED1.9 inch Thời lượng pin:  Khoảng 36 giờ (ở chế độ Năng lượng thấp)Khoảng 18 giờ (ở chế độ sử dụng thông thường) Kết nối với hệ điều hành:  iPhone Xs trở lên chạy iOS 17 trở lên Mặt:  Ion-X strengthened glass41 mm Hãng: Apple.',13990000,'images/awseries9.jpg',1,'2024-04-15 21:06:22',3,0,11192000,NULL,1),(31,'Apple Watch SE 2023 GPS','Màn hình:  OLED Thời lượng pin:  Khoảng 18 giờ (ở chế độ sử dụng thông thường) Kết nối với hệ điều hành:  iPhone Xs trở lên chạy iOS 17 trở lên Mặt:  Ion-X strengthened glass44 mm Hãng  Apple.',9990000,'images/awse23.jpg',1,'2024-04-15 21:06:22',3,0,7992000,NULL,1),(32,'Apple Watch Ultra Titanium','Màn hình:  OLED1.92 inch Thời lượng pin:  Khoảng 60 giờ (ở chế độ tiết kiệm pin)Khoảng 36 giờ (ở chế độ sử dụng thông thường) Kết nối với hệ điều hành:  iPhone 8 trở lên với iOS phiên bản mới nhất Mặt:  Kính Sapphire49 mm Hãng  Apple',23990000,'images/awultra2.jpg',1,'2024-04-15 21:06:22',3,0,19192000,NULL,1),(33,'Samsung Galaxy Tab S9 FE+','Màn hình:  12.4\"TFT LCD Hệ điều hành:  Android 13 Chip:  Exynos 1380 8 nhân RAM:  8 GB Dung lượng lưu trữ:  128 GB Camera sau:  Chính 8 MP & Phụ 8 MP Camera trước:  12 MP Pin, Sạc:  10090 mAh45 W Hãng  Samsung.',16990000,'images/ssgalaxytabs9.jpg',1,'2024-04-15 21:06:22',2,0,13592000,NULL,1),(34,'Loa Bluetooth JBL Partybox Encore 2Mic','Tổng công suất:  100 W Nguồn:  Cắm điện hoặc pin Thời gian sử dụng:  Dùng khoảng 10 tiếngSạc khoảng 3.5 tiếng Kết nối không dây:  Bluetooth 5.1 Tiện ích:  Sạc được cho thiết bị khác (cổng USB)Kết nối cùng lúc 2 loaCó đèn LEDChống nước IPX42 Micro kèm theo',10390000,'images/jblpartyboxencore2mic.jpg',1,'2024-04-15 21:06:22',4,0,8312000,NULL,1),(35,'Loa Bluetooth JBL Partybox 110','Tổng công suất:  160 W Nguồn:  Pin Thời gian sử dụng:  Dùng khoảng 12 tiếngSạc khoảng 3.5 tiếng Kết nối không dây:  Bluetooth 5.1 Tiện ích:  Điều khiển bằng điện thoạiSạc được cho thiết bị khác (cổng USB)Kết nối cùng lúc 2 loaCó đèn LEDChống nước IPX4',10990000,'images/jblpartybox110.jpg',1,'2024-04-15 21:06:22',4,0,8792000,NULL,1),(36,'Loa JBL Authentics AUTH 500','Tổng công suất:  270 W Nguồn:  200 - 240V/50 - 60Hz Kết nối không dây:  WifiBluetooth 5.3 Tiện ích:  Sạc được cho thiết bị khác (Cổng Type C)Nghe nhạc trực tuyến qua kết nối WifiKết nối cùng lúc 2 loaGoogle AssistantChống nước IPX4Alexa',16900000,'images/jblauth500.jpg',1,'2024-04-15 21:06:22',4,0,13520000,NULL,1),(37,'Lenovo Ideapad Gaming 3','CPU:  Ryzen 55500H3.3GHz RAM:  16 GBDDR4 2 khe (1 khe 8 GB + 1 khe 8 GB)3200 MHz Ổ cứng:  Hỗ trợ khe cắm HDD SATA 2.5 inch mở rộng (nâng cấp tối đa 1 TB)512 GB SSD NVMe PCIe Gen 4.0 (Có thể tháo ra, lắp thanh khác tối đa 1 TB (2280) / 512 GB (2242)) Màn h',22590000,'images/lenovoideapadgaming3.jpg',1,'2024-04-15 21:06:22',5,0,18072000,NULL,1),(38,'Iphone 15 Pro Max','Màn hình:  OLED6.7\"Super Retina XDR Hệ điều hành:  iOS 17 Camera sau:  Chính 48 MP & Phụ 12 MP, 12 MP Camera trước:  12 MP Chip:  Apple A17 Pro 6 nhân RAM:  8 GB Dung lượng lưu trữ:  1 TB SIM:  1 Nano SIM & 1 eSIMHỗ trợ 5G Pin, Sạc:  4422 mAh20 W Hãng  iP',43990000,'images/iphone15promax.jpg',1,'2024-04-15 21:06:22',1,0,35192000,NULL,1),(39,'Oppo Find N3 5G','Màn hình:  AMOLEDChính 7.82\" & Phụ 6.31\"Quad HD+ (2K+) Hệ điều hành:  Android 13 Camera sau:  Chính 48 MP & Phụ 48 MP, 64 MP Camera trước:  Trong: 20 MP & Ngoài: 32 MP Chip:  Snapdragon 8 Gen 2 8 nhân RAM:  16 GB Dung lượng lưu trữ:  512 GB SIM:  2 Nano S',41990000,'images/oppofindn3.jpg',1,'2024-04-15 21:06:22',1,0,33592000,NULL,1),(40,'Samsung Galaxy Tab S9+','Màn hình:  12.4\"Dynamic AMOLED 2X Hệ điều hành:  Android 13 Chip:  Snapdragon 8 Gen 2 for Galaxy RAM:  12 GB Dung lượng lưu trữ:  256 GB Kết nối:  5GCó nghe gọi SIM:  1 Nano SIM & 1 eSIM Camera sau:  Chính 13 MP & Phụ 8 MP Camera trước:  12 MP Pin, Sạc:  ',34990000,'images/ssgalaxytabs9plus.jpg',1,'2024-04-15 21:06:22',2,0,27992000,NULL,1),(41,'Xiaomi 14 5G','Màn hình:  AMOLED6.36\"1.5K Hệ điều hành:  Android 14 Camera sau:  Chính 50 MP & Phụ 50 MP, 50 MP Camera trước:  32 MP Chip:  Snapdragon 8 Gen 3 RAM:  12 GB Dung lượng lưu trữ:  512 GB SIM:  2 Nano SIMHỗ trợ 5G Pin, Sạc:  4610 mAh90 W Hãng  Xiaomi',31990000,'images/xiaomi145g.jpg',0,'2024-04-15 21:06:22',1,0,25592000,NULL,1),(42,'Samsung Galaxy Z Fold 5 ','Màn hình:  Dynamic AMOLED 2XChính 7.6\" & Phụ 6.2\"Quad HD+ (2K+) Hệ điều hành:  Android 13 Camera sau:  Chính 50 MP & Phụ 12 MP, 10 MP Camera trước:  10 MP & 4 MP Chip:  Snapdragon 8 Gen 2 for Galaxy RAM:  12 GB Dung lượng lưu trữ:  1 TB SIM:  2 Nano SIM h',48990000,'images/ssgalaxyzfold5.jpg',1,'2024-04-18 03:06:03',1,0,39192000,NULL,1),(43,'Sạc Apple',NULL,550000,'images/sacapple.jpg',1,'2024-04-18 04:08:52',7,0,440000,NULL,1),(44,'Sạc Samsung',NULL,475000,'images/sacsamsung.jpg',1,'2024-04-18 04:08:52',7,0,380000,NULL,1),(45,'Cáp Type C Apple ',NULL,375000,'images/captypecapple.jpg',1,'2024-04-18 04:08:52',7,0,300000,NULL,1),(46,'Cáp Lightning',NULL,369000,'images/caplightning.jpg',1,'2024-04-18 04:08:52',7,0,295200,NULL,1),(47,'Cáp Type C',NULL,275000,'images/captypec.jpg',1,'2024-04-18 04:08:52',7,0,220000,NULL,1),(48,'Cáp Micro USB',NULL,179000,'images/capmicrousb.jpg',1,'2024-04-18 04:08:52',7,0,143200,NULL,1),(49,'Sạc dự phòng Baseus ioTa BPE45A ',NULL,5450000,'images/sacbaseus.jpg',1,'2024-04-18 04:08:52',7,0,4360000,NULL,1),(50,'Sạc dự phòng Samsung EB-P3400 ',NULL,980000,'images/sacduphongsamsung.jpg',1,'2024-04-18 04:08:52',7,0,784000,NULL,1),(51,'Tai nghe Shokz OPENRUN S803 ',NULL,3490000,'images/taingheshokz2.jpg',1,'2024-04-18 04:08:52',6,0,2792000,NULL,1),(52,'Tai nghe  Denon Perl Pro AHC15PLBKEM',NULL,8490000,'images/tainghedenon.jpg',1,'2024-04-18 04:08:52',6,0,6792000,NULL,1),(53,'Chuột Bluetooth Apple MK2E3 ',NULL,1790000,'images/chuotapple.jpg',1,'2024-04-18 04:08:52',8,0,1432000,NULL,1),(54,'Chuột  Gaming ASUS ROG Keris Aimpoint',NULL,2690000,'images/chuotasus1.jpg',1,'2024-04-18 04:08:52',8,0,2152000,NULL,1),(55,'Chuột Gaming ASUS ROG Gladius III',NULL,2290000,'images/chuotasus2.jpg',1,'2024-04-18 04:08:52',8,0,1832000,NULL,1),(57,'Chuột Gaming MSI Clutch GM41 Lightweight V2',NULL,1490000,'images/chuotmsi.jpg',1,'2024-04-18 04:08:52',8,0,1192000,NULL,1),(58,'Chuột Silent Logitech Signature M650 ',NULL,1190000,'images/chuotlogitech.jpg',1,'2024-04-18 04:08:52',8,0,952000,NULL,1),(59,'Bàn phím Gaming Asus ROG Strix Scope NX TKL',NULL,3320000,'images/banphimasus.jpg',0,'2024-04-18 04:08:52',9,0,2656000,NULL,1),(60,'Bàn phím Apple Magic Keyboard',NULL,3240000,'images/banphimapple.jpg',1,'2024-04-18 04:08:52',9,0,2592000,NULL,1),(61,'Bàn Phím Gaming Razer Huntsman Tournamen',NULL,2485000,'images/banphimrazer.jpg',1,'2024-04-18 04:08:52',9,0,1988000,NULL,1),(62,'Bàn Phím Gaming MSI Vigor GK50 Elite',NULL,2250000,'images/banphimmsi.jpg',1,'2024-04-18 04:08:52',9,0,1800000,NULL,1),(63,'Bàn Phím Bluetooth Rapoo V700 - 8A',NULL,1390000,'images/banphimrapoo.jpg',1,'2024-04-18 04:08:52',9,0,1112000,NULL,1),(64,'Bàn Phím Bluetooth Dareu EK75 Pro',NULL,990000,'images/banphimdareu.jpg',0,'2024-04-18 04:08:52',9,0,792000,NULL,1),(65,'Bàn Phím Gaming Asus TUF K1',NULL,850000,'images/banphimasus2.jpg',1,'2024-04-18 04:08:52',9,0,680000,NULL,1),(66,'Ốp lưng iPhone 15 Pro Max Nhựa dẻo TPU Mipow Ultra',NULL,520000,'images/olip15.jpg',1,'2024-04-18 04:08:52',10,0,416000,NULL,1),(67,'Ốp lưng MagSafe iPhone 15 Pro Max Nhựa',NULL,1100000,'images/olip152.jpg',1,'2024-04-18 04:08:52',10,0,880000,NULL,1),(68,'Ốp lưng MagSafe iPhone 15 Pro Max Nhựa cứng',NULL,320000,'images/olip153.jpg',1,'2024-04-18 04:08:52',10,0,256000,NULL,1),(69,'Ốp lưng Magsafe iPhone 15 Pro Max Vải tinh dệt',NULL,1090000,'images/olip154.jpg',1,'2024-04-18 04:08:52',10,0,872000,NULL,1),(70,'Ốp lưng MagSafe iPhone 15 Pro Max IML UNI',NULL,665000,'images/olip155.jpg',1,'2024-04-18 04:08:52',10,0,532000,NULL,1),(71,'Ốp lưng Magsafe Galaxy Z Fold5 Nhựa cứng PC Araree',NULL,1090000,'images/opss1.jpg',0,'2024-04-18 04:08:52',10,0,872000,NULL,1),(72,'Ốp lưng Galaxy Z Fold5 Nhựa cứng viền dẻo Samsung ',NULL,780000,'images/olss2.jpg',1,'2024-04-18 04:08:52',10,0,624000,NULL,1),(73,'Ốp lưng Galaxy Z Fold5 Da ECO Samsung',NULL,1950000,'images/olss3.jpg',1,'2024-04-18 04:08:52',10,0,1560000,NULL,1),(74,'Ốp lưng Galaxy Z Fold5 Samsung  Kèm S Pen ',NULL,1295000,'images/olss4.jpg',1,'2024-04-18 04:08:52',10,0,1036000,NULL,1),(75,'Bao da Galaxy Tab S9+ / Tab S9 FE+ Samsung ',NULL,2079000,'images/optabs9.jpg',1,'2024-04-18 04:08:52',10,0,1663200,NULL,1),(76,'Bao da Pad Pro 12.9 inch ESR Rebound Hybrid ',NULL,1390000,'images/opipadpro1.jpg',0,'2024-04-18 04:08:52',10,0,1112000,NULL,1),(77,'Bao da iPad Pro 11 inch ESR Rebound Hybrid',NULL,1250000,'images/opipadpro2.jpg',1,'2024-04-18 04:08:52',10,0,1000000,NULL,1),(78,'iPad Pro M2 11 inch WiFi ',NULL,27990000,'images/ipadpro11inch.jpg',1,'2024-04-18 04:08:52',2,0,22392000,NULL,1),(79,'Bao da Galaxy A54 Smart Clear View Samsung',NULL,779000,'images/opa541.jpg',0,'2024-04-18 04:08:52',10,0,623200,NULL,1),(80,'Ốp lưng Galaxy A54 Silicone Samsung',NULL,390000,'images/opa542.jpg',1,'2024-04-18 04:08:52',10,0,312000,NULL,1),(81,'Bao da nắp gập iPad 10 UniQ Camden',NULL,849000,'images/opipad10.jpg',1,'2024-04-18 04:08:52',10,0,679200,NULL,1),(82,'Bao da nắp gập iPad Pro 11 inch UNIQ Rovus Magneti',NULL,1170000,'images/baoipadpro11.jpg',1,'2024-04-18 04:08:52',10,0,936000,NULL,1),(83,'Samsung Galaxy Watch4 40mm','Màn hình:  SUPER AMOLED1.2 inch Thời lượng pin:  Khoảng 1.5 ngày Kết nối với hệ điều hành:  Android 7.0 trở lên dùng Google Mobile Service Mặt:  Kính cường lực Gorilla Glass Dx+40 mm Hãng  Samsung',3990000,'images/ssgalaxywatch4.jpg',1,'2024-04-22 18:07:12',3,0,3192000,NULL,1),(630229,'Iphone 16 ','Công nghệ màn hình:\r\nOLED\r\nĐộ phân giải:\r\nSuper Retina XDR (1206 x 2622 Pixels)\r\nMàn hình rộng:\r\n6.3\" - Tần số quét 120 Hz\r\nĐộ sáng tối đa:\r\n2000 nits\r\nMặt kính cảm ứng:\r\nKính cường lực Ceramic Shield\r\n                  ',57600000,'images/iphone16.jpg',1,'2024-10-08 08:13:45',1,1,48000000,'0',0),(630867,' Samsung Galaxy Watch5 40mm','Công nghệ màn hình:\r\nSuper AMOLED\r\nKích thước màn hình:\r\n1.2 inch\r\nĐộ phân giải:\r\n396 x 396 pixels\r\nKích thước mặt:\r\n40 mm\r\n                  ',4320000,'images/samsung-galaxy-watch5-tn-600x600.jpg',1,'2024-10-08 08:27:32',3,2,3600000,'0',0);
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promotion`
--

DROP TABLE IF EXISTS `promotion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promotion` (
  `id` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `apply_for` enum('Product','Receipt') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promotion`
--

LOCK TABLES `promotion` WRITE;
/*!40000 ALTER TABLE `promotion` DISABLE KEYS */;
INSERT INTO `promotion` VALUES ('1','Giảm giá','2024-10-10 13:07:37','2024-10-17 13:07:37','Product'),('2','Mua 1 tặng 1','2024-10-10 13:07:37','2024-10-17 13:07:37','Product'),('3','Giá cố định','2024-10-10 13:07:37',NULL,'Product'),('4','Tặng cáp sạc khi mua Iphone 16','2024-10-09 09:07:13','2024-10-10 09:07:13','Product'),('5','Giảm 10% đối với hóa đơn trên 2 triệu','2024-10-11 09:07:13','2024-10-26 00:00:00','Receipt');
/*!40000 ALTER TABLE `promotion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promotion_detail`
--

DROP TABLE IF EXISTS `promotion_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promotion_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `discount_type` enum('PERCENTAGE','GET_FREE','FIXED_AMOUNT') NOT NULL,
  `discount_value` float DEFAULT NULL,
  `promotion_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `promotion_detail_ibfk_1_idx` (`promotion_id`),
  CONSTRAINT `promotion_detail_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promotion_detail`
--

LOCK TABLES `promotion_detail` WRITE;
/*!40000 ALTER TABLE `promotion_detail` DISABLE KEYS */;
INSERT INTO `promotion_detail` VALUES (1,1,'PERCENTAGE',13,'1'),(2,2,'GET_FREE',1,'2'),(3,3,'FIXED_AMOUNT',0,'3'),(4,4,'FIXED_AMOUNT',0,'3'),(5,16,'FIXED_AMOUNT',0,'3'),(6,17,'FIXED_AMOUNT',0,'3'),(7,20,'FIXED_AMOUNT',0,'3'),(8,21,'FIXED_AMOUNT',0,'3'),(9,22,'FIXED_AMOUNT',0,'3'),(10,23,'FIXED_AMOUNT',0,'3'),(11,24,'FIXED_AMOUNT',0,'3'),(12,25,'FIXED_AMOUNT',0,'3'),(13,26,'FIXED_AMOUNT',0,'3'),(14,27,'FIXED_AMOUNT',0,'3'),(15,28,'FIXED_AMOUNT',0,'3'),(16,29,'FIXED_AMOUNT',0,'3'),(17,30,'FIXED_AMOUNT',0,'3'),(18,31,'FIXED_AMOUNT',0,'3'),(19,32,'FIXED_AMOUNT',0,'3'),(20,33,'FIXED_AMOUNT',0,'3'),(21,34,'FIXED_AMOUNT',0,'3'),(22,35,'FIXED_AMOUNT',0,'3'),(23,36,'FIXED_AMOUNT',0,'3'),(24,37,'FIXED_AMOUNT',0,'3'),(25,38,'FIXED_AMOUNT',0,'3'),(26,39,'FIXED_AMOUNT',0,'3'),(27,40,'FIXED_AMOUNT',0,'3'),(28,41,'FIXED_AMOUNT',0,'3'),(29,42,'FIXED_AMOUNT',0,'3'),(30,43,'FIXED_AMOUNT',0,'3'),(31,44,'FIXED_AMOUNT',0,'3'),(32,45,'FIXED_AMOUNT',0,'3'),(33,46,'FIXED_AMOUNT',0,'3'),(34,47,'FIXED_AMOUNT',0,'3'),(35,48,'FIXED_AMOUNT',0,'3'),(36,49,'FIXED_AMOUNT',0,'3'),(37,50,'FIXED_AMOUNT',0,'3'),(38,51,'FIXED_AMOUNT',0,'3'),(39,52,'FIXED_AMOUNT',0,'3'),(40,53,'FIXED_AMOUNT',0,'3'),(41,54,'FIXED_AMOUNT',0,'3'),(42,55,'FIXED_AMOUNT',0,'3'),(43,57,'FIXED_AMOUNT',0,'3'),(44,58,'FIXED_AMOUNT',0,'3'),(45,59,'FIXED_AMOUNT',0,'3'),(46,60,'FIXED_AMOUNT',0,'3'),(47,61,'FIXED_AMOUNT',0,'3'),(48,62,'FIXED_AMOUNT',0,'3'),(49,63,'FIXED_AMOUNT',0,'3'),(50,64,'FIXED_AMOUNT',0,'3'),(51,65,'FIXED_AMOUNT',0,'3'),(52,66,'FIXED_AMOUNT',0,'3'),(53,67,'FIXED_AMOUNT',0,'3'),(54,68,'FIXED_AMOUNT',0,'3'),(55,69,'FIXED_AMOUNT',0,'3'),(56,70,'FIXED_AMOUNT',0,'3'),(57,71,'FIXED_AMOUNT',0,'3'),(58,72,'FIXED_AMOUNT',0,'3'),(59,73,'FIXED_AMOUNT',0,'3'),(60,74,'FIXED_AMOUNT',0,'3'),(61,75,'FIXED_AMOUNT',0,'3'),(62,76,'FIXED_AMOUNT',0,'3'),(63,77,'FIXED_AMOUNT',0,'3'),(64,78,'FIXED_AMOUNT',0,'3'),(65,79,'FIXED_AMOUNT',0,'3'),(66,80,'FIXED_AMOUNT',0,'3'),(67,81,'FIXED_AMOUNT',0,'3'),(68,82,'FIXED_AMOUNT',0,'3'),(69,83,'FIXED_AMOUNT',0,'3'),(70,630229,'FIXED_AMOUNT',0,'3'),(71,630867,'FIXED_AMOUNT',0,'3');
/*!40000 ALTER TABLE `promotion_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provider`
--

DROP TABLE IF EXISTS `provider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `provider` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provider`
--

LOCK TABLES `provider` WRITE;
/*!40000 ALTER TABLE `provider` DISABLE KEYS */;
INSERT INTO `provider` VALUES (1,'Công ty Samsung Việt Nam','Khu công nghiệp Yên Phong I, Xã Yên Trung, Huyện Yên Phong, Tỉnh Bắc Ninh'),(2,'Công ty Daewoo Việt Nam','Khu sản xuất Tân Định, Phường Tân Định, Thị Xã Bến Cát, Bình Dương'),(3,'Công ty điện tử ABECO','Số 48,Đường Hoa Bằng Lăng,Khu Đô Thị Long Việt,Thị Trấn Quang Minh,Huyện Mê Linh,Hà Nội'),(4,'Công ty Thiên Bảo','Số 7A, Đường 71, Ấp Tân Bình, Xã Bình Minh, Huyện Trảng Bom, Tỉnh Đồng Nai.'),(5,'Công ty Robotics','477 Quang Trung, P.10, Q.Gò Vấp, TPHCM'),(6,'Công ty TCL','Số 26 VSIP II-A, Đường số 32, Khu công nghiệp Việt Nam - Singapore II-A, Xã Tân Bình, Huyện Bắc Tân Uyên, Tỉnh Bình Dương.');
/*!40000 ALTER TABLE `provider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receipt`
--

DROP TABLE IF EXISTS `receipt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receipt` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_date` datetime DEFAULT NULL,
  `user_id` int NOT NULL,
  `payment_id` int NOT NULL,
  `status_id` int NOT NULL,
  `exported` tinyint(1) DEFAULT NULL,
  `delivery_address` varchar(255) NOT NULL,
  `receiver_name` varchar(255) DEFAULT NULL,
  `promotion_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `receipt_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receipt`
--

LOCK TABLES `receipt` WRITE;
/*!40000 ALTER TABLE `receipt` DISABLE KEYS */;
INSERT INTO `receipt` VALUES (2,'2024-02-18 21:43:25',7,1,2,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(4,'2024-04-22 21:59:24',1,3,6,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(6,'2024-04-23 03:24:20',8,2,3,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(7,'2024-09-09 08:05:56',9,4,4,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(16,'2024-09-19 01:01:37',9,3,2,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(17,'2024-09-19 01:01:37',9,2,1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(18,'2024-09-19 03:23:32',9,1,1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(19,'2024-09-19 03:32:32',9,1,1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(20,'2024-09-19 03:32:32',9,1,2,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(21,'2024-09-19 03:39:09',8,1,2,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(22,'2024-09-20 15:26:30',1,1,2,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(23,'2024-09-20 16:15:46',1,1,3,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(24,'2024-09-20 16:25:18',1,1,2,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(25,'2024-09-27 22:19:10',1,1,6,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(26,'2024-09-27 22:21:16',1,1,6,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(27,'2024-09-27 22:21:16',1,1,6,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(28,'2024-09-27 22:22:39',1,1,1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(29,'2024-09-27 22:22:39',1,1,6,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh',NULL,NULL),(30,'2024-09-29 02:20:39',1,2,1,1,'C13/15D Cư Xá Phú Lâm B, phường 13, quận 6, TP Hồ Chí Minh',NULL,NULL),(32,'2024-09-30 11:42:00',1,1,6,1,'629 KDV, phường An Lạc, quận Bình Tân, TPHCM','Thái Tuấn',NULL),(33,'2024-10-07 13:53:49',1,1,1,1,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh','Thái Tuấn',NULL),(34,'2024-10-07 23:39:27',1,1,6,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh','Thái Tuấn',NULL),(36,'2024-10-08 14:28:35',1,1,1,0,'629 Kinh Dương Vương, phường An Lạc, quận Bình Tân, TP Hồ Chí Minh','Thái Tuấn',NULL);
/*!40000 ALTER TABLE `receipt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receipt_detail`
--

DROP TABLE IF EXISTS `receipt_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receipt_detail` (
  `receipt_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int DEFAULT NULL,
  `unit_price` float DEFAULT NULL,
  `discount` float DEFAULT NULL,
  `discount_info` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`receipt_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `receipt_detail_ibfk_1` FOREIGN KEY (`receipt_id`) REFERENCES `receipt` (`id`),
  CONSTRAINT `receipt_detail_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receipt_detail`
--

LOCK TABLES `receipt_detail` WRITE;
/*!40000 ALTER TABLE `receipt_detail` DISABLE KEYS */;
INSERT INTO `receipt_detail` VALUES (2,17,4,26990000,NULL,NULL),(2,49,3,5450000,NULL,NULL),(4,2,1,34550000,NULL,NULL),(4,4,1,27990000,NULL,NULL),(4,23,1,25990000,NULL,NULL),(4,25,1,25690000,NULL,NULL),(4,26,1,12990000,NULL,NULL),(4,39,1,41990000,NULL,NULL),(4,42,1,48990000,NULL,NULL),(6,43,1,550000,NULL,NULL),(6,44,1,475000,NULL,NULL),(6,45,1,375000,NULL,NULL),(6,46,1,369000,NULL,NULL),(6,47,1,275000,NULL,NULL),(6,48,1,179000,NULL,NULL),(6,50,1,750000,NULL,NULL),(6,68,1,299000,NULL,NULL),(6,69,1,1090000,NULL,NULL),(6,71,1,989000,NULL,NULL),(6,73,1,1780000,NULL,NULL),(7,1,1,15990000,NULL,NULL),(7,16,5,22990000,NULL,NULL),(16,42,4,48990000,NULL,NULL),(17,31,1,9990000,NULL,NULL),(18,3,4,13990000,NULL,NULL),(19,17,3,26990000,NULL,NULL),(20,38,1,43990000,NULL,NULL),(21,3,1,13990000,NULL,NULL),(22,3,1,13990000,NULL,NULL),(23,24,3,20990000,NULL,NULL),(24,22,4,38900000,NULL,NULL),(25,1,2,14392000,0,NULL),(25,3,1,13990000,0,NULL),(25,16,1,18392000,0,NULL),(26,24,2,20990000,20990000,NULL),(27,24,7,20990000,83960000,NULL),(28,24,5,20990000,41980000,NULL),(29,3,1,13990000,0,NULL),(29,16,1,18392000,0,NULL),(30,16,1,18392000,0,NULL),(30,24,2,20990000,20990000,NULL),(30,38,1,35192000,0,NULL),(32,1,1,15291500,0,NULL),(32,2,1,27990000,0,NULL),(32,24,2,20990000,20990000,'Mua 1 tặng 1'),(33,1,1,15291500,0,NULL),(34,77,2,1250000,1250000,'Mua 1 tặng 1'),(36,1,1,15651300,0,NULL),(36,2,2,36990000,36990000,'Mua 1 tặng 1');
/*!40000 ALTER TABLE `receipt_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receipt_report`
--

DROP TABLE IF EXISTS `receipt_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receipt_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_report` int NOT NULL,
  `receipt_report` int NOT NULL,
  `description` varchar(255) NOT NULL,
  `created_date` datetime DEFAULT NULL,
  `report_type` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_report` (`user_report`),
  KEY `receipt_report` (`receipt_report`),
  CONSTRAINT `receipt_report_ibfk_1` FOREIGN KEY (`user_report`) REFERENCES `user` (`id`),
  CONSTRAINT `receipt_report_ibfk_2` FOREIGN KEY (`receipt_report`) REFERENCES `receipt` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receipt_report`
--

LOCK TABLES `receipt_report` WRITE;
/*!40000 ALTER TABLE `receipt_report` DISABLE KEYS */;
INSERT INTO `receipt_report` VALUES (1,1,23,'chua nhan duoc','2024-09-20 17:22:29',2),(2,1,24,'chua nhan dc','2024-09-20 17:23:43',1),(3,1,24,'chua nhan dc','2024-09-20 17:24:21',1),(4,1,24,'haha','2024-09-20 18:20:04',2),(5,1,24,'chua nhan dc','2024-09-20 18:21:29',1),(6,1,24,'chua nhan dc','2024-09-20 18:21:29',2),(7,1,24,'','2024-09-20 18:21:29',2),(8,1,24,'','2024-09-20 18:21:29',1),(9,1,24,'','2024-09-20 18:21:29',2),(10,1,23,'awdawd','2024-09-20 18:21:29',2),(11,1,24,'','2024-09-20 18:21:29',2),(12,1,23,'Chua nhan dc hang','2024-09-20 18:34:11',1),(13,8,21,'chua nhan dc','2024-09-24 19:57:51',1),(14,1,36,'bkj,nklnl ','2024-10-14 13:06:28',1);
/*!40000 ALTER TABLE `receipt_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receipt_status`
--

DROP TABLE IF EXISTS `receipt_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receipt_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receipt_status`
--

LOCK TABLES `receipt_status` WRITE;
/*!40000 ALTER TABLE `receipt_status` DISABLE KEYS */;
INSERT INTO `receipt_status` VALUES (1,'Đang giao'),(2,'Đã hoàn thành'),(3,'Cần hỗ trợ'),(4,'Đã hủy'),(5,'Chờ xác nhận hoàn thành'),(6,'Chờ xác nhận xuất kho');
/*!40000 ALTER TABLE `receipt_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_type`
--

DROP TABLE IF EXISTS `report_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_type`
--

LOCK TABLES `report_type` WRITE;
/*!40000 ALTER TABLE `report_type` DISABLE KEYS */;
INSERT INTO `report_type` VALUES (1,'Thời gian giao hàng'),(2,'Sản phẩm trong đơn hàng'),(3,'Hủy đơn hàng'),(4,'Đổi/trả sản phẩm');
/*!40000 ALTER TABLE `report_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `avatar` varchar(100) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `joined_date` datetime DEFAULT NULL,
  `phone_number` varchar(11) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Thai Tuan','tuan171204','202cb962ac59075b964b07152d234b70','https://avatar.iran.liara.run/public/17','titofood17122004@gmail.com',1,'2024-04-09 18:15:26','0902451316',NULL),(7,'Thai Tuan','tuan171205','202cb962ac59075b964b07152d234b70','https://avatar.iran.liara.run/public/11','titofood17122004@gmail.com',1,'2024-04-16 20:20:22','',NULL),(8,'Obama','Obama','202cb962ac59075b964b07152d234b70','https://avatar.iran.liara.run/public/30','titofood17122004@gmail.com',1,'2024-04-16 20:34:14','',NULL),(9,'Tuan Thai','t171204','202cb962ac59075b964b07152d234b70','https://avatar.iran.liara.run/public/8','thaituandz17122004@gmail.com',0,'2024-09-09 08:05:56','',NULL),(10,'t171205','t171205','202cb962ac59075b964b07152d234b70','https://avatar.iran.liara.run/public/73','thaituandz17122004@gmail.com',1,'2024-09-15 01:11:50','',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_role`
--

DROP TABLE IF EXISTS `user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `view_customer` tinyint(1) DEFAULT NULL,
  `view_receipt` tinyint(1) DEFAULT NULL,
  `view_stats` tinyint(1) DEFAULT NULL,
  `update_receipt` tinyint(1) DEFAULT NULL,
  `view_product` tinyint(1) DEFAULT NULL,
  `update_product` tinyint(1) DEFAULT NULL,
  `order_product` tinyint(1) DEFAULT NULL,
  `receive_product` tinyint(1) DEFAULT NULL,
  `view_user` tinyint(1) DEFAULT NULL,
  `login_admin` tinyint(1) DEFAULT NULL,
  `privileged` tinyint(1) DEFAULT NULL,
  `super_user` tinyint(1) DEFAULT NULL,
  `delivery_product` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_role`
--

LOCK TABLES `user_role` WRITE;
/*!40000 ALTER TABLE `user_role` DISABLE KEYS */;
INSERT INTO `user_role` VALUES (1,1,1,1,1,1,1,1,1,1,1,1,1,1),(2,0,0,0,0,0,0,0,0,0,0,0,0,0),(3,1,1,0,0,0,0,0,1,0,1,0,0,0),(4,0,0,0,0,0,0,0,0,0,0,0,0,0),(5,0,0,0,0,0,0,0,0,0,0,0,0,0);
/*!40000 ALTER TABLE `user_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ward`
--

DROP TABLE IF EXISTS `ward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ward` (
  `id` int NOT NULL AUTO_INCREMENT,
  `district_id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  CONSTRAINT `ward_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `district` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=242 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ward`
--

LOCK TABLES `ward` WRITE;
/*!40000 ALTER TABLE `ward` DISABLE KEYS */;
INSERT INTO `ward` VALUES (1,1,'Phường Tân Định'),(2,1,'Phường Đa Kao'),(3,1,'Phường Bến Nghé'),(4,1,'Phường Bến Thành'),(5,1,'Phường Nguyễn Thái Bình'),(6,1,'Phường Phạm Ngũ Lão'),(7,1,'Phường Cô Giang'),(8,1,'Phường Cầu Kho'),(9,1,'Phường Cầu Ông Lãnh'),(10,2,'Phường Võ Thị Sáu'),(11,2,'Phường 1'),(12,2,'Phường 2'),(13,2,'Phường 3'),(14,2,'Phường 4'),(15,2,'Phường 5'),(16,2,'Phường 9'),(17,2,'Phường 11'),(18,2,'Phường 12'),(19,2,'Phường 13'),(20,3,'Phường 1'),(21,3,'Phường 2'),(22,3,'Phường 3'),(23,3,'Phường 4'),(24,3,'Phường 6'),(25,3,'Phường 8'),(26,3,'Phường 9'),(27,3,'Phường 13'),(28,3,'Phường 16'),(29,3,'Phường 18'),(30,4,'Phường 1'),(31,4,'Phường 2'),(32,4,'Phường 3'),(33,4,'Phường 4'),(34,4,'Phường 5'),(35,4,'Phường 6'),(36,4,'Phường 7'),(37,4,'Phường 8'),(38,4,'Phường 9'),(39,4,'Phường 10'),(40,4,'Phường 11'),(41,4,'Phường 12'),(42,4,'Phường 13'),(43,5,'Phường Tân Thuận Đông'),(44,5,'Phường Tân Thuận Tây'),(45,5,'Phường Tân Kiểng'),(46,5,'Phường Tân Hưng'),(47,5,'Phường Tân Phong'),(48,5,'Phường Tân Quy'),(49,5,'Phường Tân Phú'),(50,5,'Phường Bình Thuận'),(51,5,'Phường Phú Mỹ'),(52,6,'Phường 1'),(53,6,'Phường 2'),(54,6,'Phường 3'),(55,6,'Phường 5'),(56,6,'Phường 6'),(57,6,'Phường 7'),(58,6,'Phường 11'),(59,6,'Phường 12'),(60,6,'Phường 13'),(61,6,'Phường 14'),(62,6,'Phường 15'),(63,6,'Phường 17'),(64,6,'Phường 19'),(65,6,'Phường 21'),(66,6,'Phường 22'),(67,7,'Phường Bình Chiểu'),(68,7,'Phường Bình Thọ'),(69,7,'Phường Hiệp Bình Chánh'),(70,7,'Phường Hiệp Bình Phước'),(71,7,'Phường Linh Chiểu'),(72,7,'Phường Linh Đông'),(73,7,'Phường Linh Tây'),(74,7,'Phường Linh Trung'),(75,7,'Phường Linh Xuân'),(76,7,'Phường Tam Bình'),(77,7,'Phường Tam Phú'),(78,7,'Phường Trường Thọ'),(79,8,'Phường 1'),(80,8,'Phường 3'),(81,8,'Phường 4'),(82,8,'Phường 5'),(83,8,'Phường 6'),(84,8,'Phường 7'),(85,8,'Phường 8'),(86,8,'Phường 9'),(87,8,'Phường 10'),(88,8,'Phường 11'),(89,8,'Phường 12'),(90,8,'Phường 13'),(91,8,'Phường 14'),(92,8,'Phường 15'),(93,8,'Phường 16'),(94,8,'Phường 17'),(95,9,'Phường An Khánh'),(96,9,'Phường Thủ Thiêm'),(97,9,'Phường An Lợi Đông'),(98,9,'Phường An Phú'),(99,9,'Phường Bình An'),(100,9,'Phường Bình Khánh'),(101,9,'Phường Bình Trưng Đông'),(102,9,'Phường Bình Trưng Tây'),(103,9,'Phường Cát Lái'),(104,9,'Phường Thạnh Mỹ Lợi'),(105,9,'Phường Thảo Điền'),(106,9,'Phường Thủ Thiêm'),(107,10,'Phường 1'),(108,10,'Phường 2'),(109,10,'Phường 3'),(110,10,'Phường 4'),(111,10,'Phường 5'),(112,10,'Phường 6'),(113,10,'Phường 7'),(114,10,'Phường 8'),(115,10,'Phường 9'),(116,10,'Phường 10'),(117,10,'Phường 11'),(118,10,'Phường 12'),(119,10,'Phường 13'),(120,11,'Phường 1'),(121,11,'Phường 2'),(122,11,'Phường 3'),(123,11,'Phường 4'),(124,11,'Phường 5'),(125,11,'Phường 6'),(126,11,'Phường 7'),(127,11,'Phường 8'),(128,11,'Phường 9'),(129,11,'Phường 10'),(130,11,'Phường 11'),(131,11,'Phường 12'),(132,11,'Phường 13'),(133,11,'Phường 14'),(134,11,'Phường 15'),(135,11,'Phường 16'),(136,12,'Phường Hiệp Phú'),(137,12,'Phường Long Bình'),(138,12,'Phường Long Phước'),(139,12,'Phường Long Thạnh Mỹ'),(140,12,'Phường Long Trường'),(141,12,'Phường Phú Hữu'),(142,12,'Phường Phước Bình'),(143,12,'Phường Phước Long A'),(144,12,'Phường Phước Long B'),(145,12,'Phường Tăng Nhơn Phú A'),(146,12,'Phường Tăng Nhơn Phú B'),(147,12,'Phường Tân Phú'),(148,12,'Phường Trường Thạnh'),(149,13,'Phường 1'),(150,13,'Phường 2'),(151,13,'Phường 3'),(152,13,'Phường 4'),(153,13,'Phường 5'),(154,13,'Phường 6'),(155,13,'Phường 7'),(156,13,'Phường 8'),(157,13,'Phường 9'),(158,13,'Phường 10'),(159,13,'Phường 11'),(160,13,'Phường 12'),(161,13,'Phường 13'),(162,13,'Phường 14'),(163,13,'Phường 15'),(164,14,'Phường 1'),(165,14,'Phường 2'),(166,14,'Phường 3'),(167,14,'Phường 4'),(168,14,'Phường 5'),(169,14,'Phường 6'),(170,14,'Phường 7'),(171,14,'Phường 8'),(172,14,'Phường 9'),(173,14,'Phường 10'),(174,14,'Phường 11'),(175,14,'Phường 12'),(176,14,'Phường 13'),(177,14,'Phường 14'),(178,14,'Phường 15'),(179,14,'Phường 16'),(180,15,'Phường An Phú Đông'),(181,15,'Phường Đông Hưng Thuận'),(182,15,'Phường Hiệp Thành'),(183,15,'Phường Tân Chánh Hiệp'),(184,15,'Phường Tân Hưng Thuận'),(185,15,'Phường Tân Thới Hiệp'),(186,15,'Phường Tân Thới Nhất'),(187,15,'Phường Thạnh Lộc'),(188,15,'Phường Thạnh Xuân'),(189,15,'Phường Thới An'),(190,15,'Phường Trung Mỹ Tây'),(191,16,'Phường An Lạc'),(192,16,'Phường An Lạc A'),(193,16,'Phường Bình Hưng Hòa'),(194,16,'Phường Bình Hưng Hòa A'),(195,16,'Phường Bình Hưng Hòa B'),(196,16,'Phường Bình Trị Đông'),(197,16,'Phường Bình Trị Đông A'),(198,16,'Phường Bình Trị Đông B'),(199,16,'Phường Tân Tạo'),(200,16,'Phường Tân Tạo A'),(201,17,'Phường 1'),(202,17,'Phường 2'),(203,17,'Phường 3'),(204,17,'Phường 4'),(205,17,'Phường 5'),(206,17,'Phường 7'),(207,17,'Phường 8'),(208,17,'Phường 9'),(209,17,'Phường 10'),(210,17,'Phường 11'),(211,17,'Phường 12'),(212,17,'Phường 13'),(213,17,'Phường 14'),(214,17,'Phường 15'),(215,17,'Phường 17'),(216,18,'Phường Hiệp Tân'),(217,18,'Phường Hòa Thạnh'),(218,18,'Phường Phú Thạnh'),(219,18,'Phường Phú Thọ Hòa'),(220,18,'Phường Phú Trung'),(221,18,'Phường Sơn Kỳ'),(222,18,'Phường Tân Qúy'),(223,18,'Phường Tân Sơn Nhì'),(224,18,'Phường Tân Thành'),(225,18,'Phường Tân Thới Hòa'),(226,18,'Phường Tây Thạnh'),(227,19,'Phường 1'),(228,19,'Phường 2'),(229,19,'Phường 3'),(230,19,'Phường 4'),(231,19,'Phường 5'),(232,19,'Phường 6'),(233,19,'Phường 7'),(234,19,'Phường 8'),(235,19,'Phường 9'),(236,19,'Phường 10'),(237,19,'Phường 11'),(238,19,'Phường 12'),(239,19,'Phường 13'),(240,19,'Phường 14'),(241,19,'Phường 15');
/*!40000 ALTER TABLE `ward` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warranty`
--

DROP TABLE IF EXISTS `warranty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warranty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(255) DEFAULT NULL,
  `warranty_period` int NOT NULL,
  `time_unit` enum('YEAR','MONTH','WEEK') NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warranty`
--

LOCK TABLES `warranty` WRITE;
/*!40000 ALTER TABLE `warranty` DISABLE KEYS */;
INSERT INTO `warranty` VALUES (1,'Đổi trả sản phẩm',12,'MONTH'),(2,'Đổi trả sản phẩm ',6,'MONTH'),(3,'Bảo trì sản phẩm ',12,'MONTH'),(4,'Bảo trì linh kiện',12,'MONTH');
/*!40000 ALTER TABLE `warranty` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-15  0:33:23
