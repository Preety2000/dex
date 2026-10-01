-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: db_main
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
-- Table structure for table `usersmeta`
--

DROP TABLE IF EXISTS `usersmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usersmeta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` int DEFAULT NULL,
  `ipinfo` text COLLATE utf8mb4_unicode_ci,
  `device` text COLLATE utf8mb4_unicode_ci,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usersmeta`
--

LOCK TABLES `usersmeta` WRITE;
/*!40000 ALTER TABLE `usersmeta` DISABLE KEYS */;
INSERT INTO `usersmeta` VALUES (7,34,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-03-12 15:10:24'),(11,36,'{\"ip\": \"57.128.191.86\", \"hostname\": \"vps-80b7be30.vps.ovh.net\", \"city\": \"Bexley\", \"region\": \"England\", \"country\": \"GB\", \"loc\": \"51.4416,0.1487\", \"org\": \"AS16276 OVH SAS\", \"postal\": \"DA15\", \"timezone\": \"Europe/London\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-03-12 15:46:17'),(12,37,'{\"ip\": \"2409:40e4:1223:e6ba:8000::\", \"city\": \"Patna\", \"region\": \"Bihar\", \"country\": \"IN\", \"loc\": \"25.5941,85.1356\", \"org\": \"AS55836 Reliance Jio Infocomm Limited\", \"postal\": \"800001\", \"timezone\": \"Asia/Kolkata\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-03-14 02:26:18'),(14,36,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-03-24 00:11:22'),(17,38,'{\"ip\": \"2401:4900:778e:93d1:800:68ff:fef0:9ac5\", \"city\": \"Patna\", \"region\": \"Bihar\", \"country\": \"IN\", \"loc\": \"25.5941,85.1356\", \"org\": \"AS45609 Bharti Airtel Ltd. AS for GPRS Service\", \"postal\": \"800001\", \"timezone\": \"Asia/Kolkata\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-03-27 15:18:28'),(30,39,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-04-28 04:48:00'),(36,39,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-19 17:08:32'),(37,34,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-21 09:59:05'),(38,36,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-21 18:07:08'),(39,40,'{\"ip\": \"2401:4900:b00d:e01f:fca5:82a7:6321:b4f1\", \"city\": \"Patna\", \"region\": \"Bihar\", \"country\": \"IN\", \"loc\": \"25.5941,85.1356\", \"org\": \"AS45609 Bharti Airtel Ltd. AS for GPRS Service\", \"postal\": \"800001\", \"timezone\": \"Asia/Kolkata\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-07-25 20:17:09'),(42,34,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-26 14:39:02'),(43,40,'{\"ip\": \"2401:4900:b467:ed69:f404:abe8:49fa:4390\", \"city\": \"Patna\", \"region\": \"Bihar\", \"country\": \"IN\", \"loc\": \"25.5941,85.1356\", \"org\": \"AS45609 Bharti Airtel Ltd. AS for GPRS Service\", \"postal\": \"800001\", \"timezone\": \"Asia/Kolkata\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-07-27 19:40:48'),(44,42,'{\"ip\": \"2401:4900:b467:ed69:88d2:fcff:feba:50a\", \"city\": \"Patna\", \"region\": \"Bihar\", \"country\": \"IN\", \"loc\": \"25.5941,85.1356\", \"org\": \"AS45609 Bharti Airtel Ltd. AS for GPRS Service\", \"postal\": \"800001\", \"timezone\": \"Asia/Kolkata\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-07-27 19:40:48'),(45,43,'{\"ip\": \"2409:40e4:1117:8ebc:8000::\", \"city\": \"Patna\", \"region\": \"Bihar\", \"country\": \"IN\", \"loc\": \"25.5941,85.1356\", \"org\": \"AS55836 Reliance Jio Infocomm Limited\", \"postal\": \"800001\", \"timezone\": \"Asia/Kolkata\", \"readme\": \"https://ipinfo.io/missingauth\"}','','2025-07-30 07:51:22'),(46,44,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-30 07:51:22'),(51,36,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-30 19:11:40'),(53,45,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-07-30 19:36:14'),(57,40,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-01 16:34:30'),(58,34,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-01 17:31:46'),(59,39,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-05 08:06:46'),(62,33,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-08 04:58:31'),(63,33,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-08 08:11:37'),(67,33,'{}','','2025-08-09 17:49:30'),(68,33,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-10 03:54:35'),(69,41,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-10 04:49:15'),(70,40,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-10 04:49:15'),(71,41,'{\"ip\": \"192.168.17.207\", \"bogon\": true}','','2025-08-10 17:41:43'),(72,41,'{\"ip\": \"192.168.17.207\", \"bogon\": true}','','2025-08-10 17:41:43'),(73,46,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-12 06:11:49'),(74,47,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-12 06:57:55'),(76,48,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-12 07:14:16'),(77,48,'{\"ip\": \"127.0.0.1\", \"bogon\": true}','','2025-08-12 07:55:17'),(78,48,'\"127.0.0.1\"','','2025-08-12 09:03:12'),(79,48,'\"127.0.0.1\"','','2025-08-12 09:23:05'),(80,41,'\"192.168.17.207\"','','2025-08-12 09:27:51');
/*!40000 ALTER TABLE `usersmeta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-06 10:28:04
