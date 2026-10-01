-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: db_hindi
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
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text COLLATE utf8mb4_unicode_ci,
  `excerpt` text COLLATE utf8mb4_unicode_ci,
  `writer` int DEFAULT NULL,
  `subject` int DEFAULT NULL,
  `image_src` text COLLATE utf8mb4_unicode_ci,
  `slug` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'विश्व का इतिहास','यह पुस्तक मानव सभ्यता के आरंभ से लेकर वर्तमान तक का इतिहास प्रस्तुत करती है, जिसमें सामाजिक, राजनीतिक, आर्थिक, भौगोलिक, सांस्कृतिक और धार्मिक पहलुओं को शामिल किया गया है.',0,1,'empty.png','world-history'),(2,'प्राचीन भारत का इतिहास','प्राचीन भारत का इतिहास, मानव सभ्यता के उदय से लेकर मुस्लिम शासकों के आने से पहले तक का इतिहास है. यह इतिहास बहुत पुराना है और पाषाण युग से शुरू हुआ माना जाता है. प्राचीन भारत के इतिहास के बारे में ज़्यादा जानकारी पाने के लिए, आप ये किताबें पढ़ सकते हैं',0,1,'empty.png','history-of-ancient-india'),(3,'मध्यकालीन भारत के इतिहास','मध्यकालीन भारत का इतिहास, प्राचीन भारत और आधुनिक भारत के बीच के काल को कहते हैं. यह काल 6वीं शताब्दी में गुप्त साम्राज्य के अंत से 1526 में मुगल साम्राज्य की शुरुआत तक का है. इस काल में कई ऐतिहासिक घटनाएं घटीं',0,1,'empty.png','history-of-medieval-india'),(4,'आधुनिक भारत का इतिहास','आधुनिक भारत का इतिहास 18वीं सदी के मध्य से शुरू होकर भारत में ब्रिटिश शासन की स्थापना और स्वतंत्रता के बाद तक का समय है। इस दौरान, मुगल साम्राज्य का पतन, यूरोपीय कंपनियों का आगमन, और ब्रिटिश शासन के अधीन भारत में हुए राजनीतिक, सामाजिक और आर्थिक बदलाव शामिल हैं\r\n\r\nप्रमुख घटनाएँ और तथ्य:\r\nमुगल साम्राज्य का पतन:\r\n18वीं शताब्दी के मध्य में मुगल साम्राज्य कमजोर होने लगा और क्षेत्रीय शक्तियाँ उभरने लगीं, जिसके बाद भारत में ब्रिटिश ईस्ट इंडिया कंपनी का प्रभाव बढ़ा. \r\nयूरोपीय कंपनियों का आगमन:\r\nपुर्तगाली, डच, अंग्रेज और फ्रांसीसियों सहित यूरोपीय कंपनियों ने भारत में व्यापार करना शुरू किया, और धीरे-धीरे उन्होंने अपना प्रभाव बढ़ाया. \r\nब्रिटिश शासन की स्थापना:\r\n1857 की क्रांति के बाद, भारत पर ब्रिटिश ताज का शासन स्थापित हुआ, जिससे राजनीतिक, सामाजिक और आर्थिक बदलाव हुए. \r\nस्वतंत्रता आंदोलन:\r\nब्रिटिश शासन के खिलाफ भारतीय स्वतंत्रता आंदोलन 19वीं शताब्दी के अंत में शुरू हुआ और 20वीं शताब्दी में तेजी से बढ़ा. \r\nभारतीय राष्ट्रीय कांग्रेस की स्थापना:\r\n1885 में भारतीय राष्ट्रीय कांग्रेस की स्थापना हुई, जिसने भारतीय स्वतंत्रता आंदोलन में महत्वपूर्ण भूमिका निभाई. \r\nस्वतंत्रता और विभाजन:\r\n15 अगस्त, 1947 को भारत को स्वतंत्रता मिली, लेकिन देश का विभाजन भी हुआ, जिससे लाखों लोग प्रभावित हुए. \r\nगणराज्य की स्थापना:\r\n26 जनवरी, 1950 को भारत एक गणराज्य बना. \r\nआधुनिक भारत में विकास:\r\nस्वतंत्रता के बाद भारत ने विभिन्न क्षेत्रों में विकास किया, जिनमें आर्थिक, सामाजिक और राजनीतिक सुधार शामिल हैं. ',0,1,'empty.png','history-of-modern-india');
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-06 10:28:00
