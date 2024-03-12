#include <Arduino.h>
#include <unity.h>

void test_encoder_gets_current_position_is_zero() { TEST_ASSERT_EQUAL(0, 0); }
void test_encoder_gets_current_position_is_not_zero() {
  TEST_ASSERT_EQUAL(0, 0);
}
void test_alarm_pins_are_not_faulty() { TEST_ASSERT_EQUAL(0, 0); }
void test_motor_connected() { TEST_ASSERT_EQUAL(0, 0); }

void setUp(void) {
  // set stuff up here
}

void tearDown(void) {
  // clean stuff up here
}

void setup() {
  delay(2000);
  UNITY_BEGIN();

  RUN_TEST(test_encoder_gets_current_position_is_zero);
  RUN_TEST(test_encoder_gets_current_position_is_not_zero);
  RUN_TEST(test_alarm_pins_are_not_faulty);
  RUN_TEST(test_motor_connected);

  UNITY_END();
}

void loop() {}
