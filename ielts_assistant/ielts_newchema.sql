-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema ielts
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `ielts` ;

-- -----------------------------------------------------
-- Schema ielts
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ielts` DEFAULT CHARACTER SET utf8mb3 ;
USE `ielts` ;

-- -----------------------------------------------------
-- Table `ielts`.`listening_passages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`listening_passages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `topic` VARCHAR(255) NULL DEFAULT NULL,
  `passage_text` TEXT NULL DEFAULT NULL,
  `audio_url` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`listening_questions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`listening_questions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `passage_id` INT NULL DEFAULT NULL,
  `question_text` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `passage_id` (`passage_id` ASC) VISIBLE,
  CONSTRAINT `listening_questions_ibfk_1`
    FOREIGN KEY (`passage_id`)
    REFERENCES `ielts`.`listening_passages` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`listening_answers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`listening_answers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL DEFAULT NULL,
  `question_id` INT NULL DEFAULT NULL,
  `answer` TEXT NULL DEFAULT NULL,
  `is_correct` TINYINT(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `question_id` (`question_id` ASC) VISIBLE,
  CONSTRAINT `listening_answers_ibfk_1`
    FOREIGN KEY (`question_id`)
    REFERENCES `ielts`.`listening_questions` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`questions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`questions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `passage` TEXT NOT NULL,
  `question_text` TEXT NOT NULL,
  `correct_answer` VARCHAR(255) NOT NULL,
  `options` TEXT NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 387
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(150) NOT NULL,
  `last_name` VARCHAR(150) NOT NULL,
  `email` VARCHAR(150) NOT NULL,
  `password` VARCHAR(150) NOT NULL,
  `verified` TINYINT(1) NULL DEFAULT '0',
  `verification_code` VARCHAR(6) NULL DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 24
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`user_answers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`user_answers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `question_id` INT NOT NULL,
  `user_answer` VARCHAR(255) NOT NULL,
  `is_correct` TINYINT(1) NOT NULL,
  `answered_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `user_id` (`user_id` ASC) VISIBLE,
  INDEX `question_id` (`question_id` ASC) VISIBLE,
  CONSTRAINT `user_answers_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `ielts`.`users` (`id`),
  CONSTRAINT `user_answers_ibfk_2`
    FOREIGN KEY (`question_id`)
    REFERENCES `ielts`.`questions` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`user_progress`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`user_progress` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `total_questions` INT NOT NULL,
  `correct_answers` INT NOT NULL,
  `score` FLOAT NOT NULL,
  `last_updated` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `user_id` (`user_id` ASC) VISIBLE,
  CONSTRAINT `user_progress_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `ielts`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 29
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`writing_responses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`writing_responses` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `module` VARCHAR(255) NOT NULL,
  `task_number` INT NOT NULL,
  `response` TEXT NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `user_id` (`user_id` ASC) VISIBLE,
  CONSTRAINT `writing_responses_ibfk_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `ielts`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 76
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `ielts`.`writing_feedback`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ielts`.`writing_feedback` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `response_id` INT NULL DEFAULT NULL,
  `feedback` JSON NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `response_id` (`response_id` ASC) VISIBLE,
  CONSTRAINT `writing_feedback_ibfk_1`
    FOREIGN KEY (`response_id`)
    REFERENCES `ielts`.`writing_responses` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
