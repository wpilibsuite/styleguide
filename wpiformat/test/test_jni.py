from wpiformat.jni import Jni

from .test_tasktest import *


def test_jni():
    # Input args go to next line even if they fit on same line
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT void JNICALL
Java_TestJNI_testFunc(JNIEnv* env, jclass) {
""",
        """/*
 * Class:     TestJNI
 * Method:    testFunc
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_TestJNI_testFunc
  (JNIEnv* env, jclass)
{
""",
        True,
    )

    # Input aligned to "(" and args past end of line
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT void JNICALL
Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent(JNIEnv* env,
                                                                 jclass,
                                                                 jint source) {
""",
        """/*
 * Class:     edu_wpi_cscore_CameraServerJNI
 * Method:    setCameraExposureHoldCurrent
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent
  (JNIEnv* env, jclass, jint source)
{
""",
        True,
    )

    # Args in input on line after "(" and args length > 80 characters
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT void JNICALL Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame(
    JNIEnv *env, jclass, jint source, jlong imageNativeObj) {
""",
        """/*
 * Class:     edu_wpi_cscore_CameraServerJNI
 * Method:    putSourceFrame
 * Signature: (IJ)V
 */
JNIEXPORT void JNICALL
Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame
  (JNIEnv *env, jclass, jint source, jlong imageNativeObj)
{
""",
        True,
    )

    # Args > 80 characters long
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT jint JNICALL Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty(
    JNIEnv *env, jclass, jint source, jstring name, jint kind, jint minimum,
    jint maximum, jint step, jint defaultValue, jint value) {
""",
        """/*
 * Class:     edu_wpi_cscore_CameraServerJNI
 * Method:    createSourceProperty
 * Signature: (ILjava/lang/String;IIIIII)I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty
  (JNIEnv *env, jclass, jint source, jstring name, jint kind, jint minimum,
   jint maximum, jint step, jint defaultValue, jint value)
{
""",
        True,
    )

    # Ensure fixes clang-format output aligned with "("
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance(JNIEnv*,
                                                                 jclass) {
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv*, jclass)
{
""",
        True,
    )

    # Idempotence for same code
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv*, jclass)
{
"""
    run_and_check_file(Jni(), "./TestJNI.cpp", contents, contents, True)

    # Idempotence for same code with named jclass variable
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv*, jclass class)
{
"""
    run_and_check_file(Jni(), "./TestJNI.cpp", contents, contents, True)

    # Check signature that breaks verbose regexes
    run_and_check_file(
        Jni(),
        "./NetworkTablesJNI.cpp",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntry
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry(JNIEnv* env, jclass,
                                                           jint inst,
                                                           jstring key) {
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntry
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry
  (JNIEnv* env, jclass, jint inst, jstring key)
{
""",
        True,
    )

    # Function with array type as argument
    run_and_check_file(
        Jni(),
        "./NetworkTablesJNI.cpp",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntries
 * Signature: (ILjava/lang/String;I)[I
 */
JNIEXPORT jintArray JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries(JNIEnv* env,
                                                             jclass, jint inst,
                                                             jstring prefix,
                                                             jint types) {
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntries
 * Signature: (ILjava/lang/String;I)[I
 */
JNIEXPORT jintArray JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries
  (JNIEnv* env, jclass, jint inst, jstring prefix, jint types)
{
""",
        True,
    )

    # Ensure functions with overloads are handled correctly
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    setRaw
 * Signature: (IJ[BZ)Z
 */
JNIEXPORT jboolean JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_setRaw__IJ_3BZ
  (JNIEnv* env, jclass, jint entry, jlong time, jbyteArray value,
   jboolean force)
{
"""
    run_and_check_file(Jni(), "./NetworkTablesJNI.cpp", contents, contents, True)

    # Ensure text before JNIEXPORT and after args and ")" is handled correctly
    # as well as two JNI functions in a row
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """/**
 *
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance
  (JNIEnv *, jclass)
{
  return nt::GetDefaultInstance();
}

JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv *, jclass)
{
  return nt::CreateInstance();
}
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getDefaultInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance
  (JNIEnv *, jclass)
{
  return nt::GetDefaultInstance();
}

/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv *, jclass)
{
  return nt::CreateInstance();
}
""",
        True,
    )

    # Handle function declarations properly
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getDefaultInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance
  (JNIEnv *, jclass);

/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv *, jclass)
{
  return nt::CreateInstance();
}
"""
    run_and_check_file(Jni(), "./TestJNI.cpp", contents, contents, True)

    # Handle functions whose arguments don't have variable names properly
    run_and_check_file(
        Jni(),
        "./DigitalGlitchFilterJNI.cpp",
        """/*
 * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI
 * Method:    cleanFilter
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter
  (JNIEnv *, jclass, jint)
{
  HAL_CleanFilter(handle);
}
""",
        """/*
 * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI
 * Method:    cleanFilter
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter
  (JNIEnv *, jclass, jint)
{
  HAL_CleanFilter(handle);
}
""",
        True,
    )

    # Input args go to next line even if they fit on same line
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT void JNICALL
Java_TestJNI_testFunc(JNIEnv* env, jobject) {
""",
        """/*
 * Class:     TestJNI
 * Method:    testFunc
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_TestJNI_testFunc
  (JNIEnv* env, jobject)
{
""",
        True,
    )

    # Input aligned to "(" and args past end of line
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT void JNICALL
Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent(JNIEnv* env,
                                                                 jobject,
                                                                 jint source) {
""",
        """/*
 * Class:     edu_wpi_cscore_CameraServerJNI
 * Method:    setCameraExposureHoldCurrent
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent
  (JNIEnv* env, jobject, jint source)
{
""",
        True,
    )

    # Args in input on line after "(" and args length > 80 characters
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT void JNICALL Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame(
    JNIEnv *env, jobject, jint source, jlong imageNativeObj) {
""",
        """/*
 * Class:     edu_wpi_cscore_CameraServerJNI
 * Method:    putSourceFrame
 * Signature: (IJ)V
 */
JNIEXPORT void JNICALL
Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame
  (JNIEnv *env, jobject, jint source, jlong imageNativeObj)
{
""",
        True,
    )

    # Args > 80 characters long
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT jint JNICALL Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty(
    JNIEnv *env, jobject, jint source, jstring name, jint kind, jint minimum,
    jint maximum, jint step, jint defaultValue, jint value) {
""",
        """/*
 * Class:     edu_wpi_cscore_CameraServerJNI
 * Method:    createSourceProperty
 * Signature: (ILjava/lang/String;IIIIII)I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty
  (JNIEnv *env, jobject, jint source, jstring name, jint kind, jint minimum,
   jint maximum, jint step, jint defaultValue, jint value)
{
""",
        True,
    )

    # Ensure fixes clang-format output aligned with "("
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance(JNIEnv*,
                                                                 jobject) {
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv*, jobject)
{
""",
        True,
    )

    # Idempotence for same code
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv*, jobject)
{
"""
    run_and_check_file(Jni(), "./TestJNI.cpp", contents, contents, True)

    # Idempotence for same code with named jobject variable
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv*, jobject class)
{
"""
    run_and_check_file(Jni(), "./TestJNI.cpp", contents, contents, True)

    # Check signature that breaks verbose regexes
    run_and_check_file(
        Jni(),
        "./NetworkTablesJNI.cpp",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntry
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry(JNIEnv* env, jobject,
                                                           jint inst,
                                                           jstring key) {
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntry
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry
  (JNIEnv* env, jobject, jint inst, jstring key)
{
""",
        True,
    )

    # Function with array type as argument
    run_and_check_file(
        Jni(),
        "./NetworkTablesJNI.cpp",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntries
 * Signature: (ILjava/lang/String;I)[I
 */
JNIEXPORT jintArray JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries(JNIEnv* env,
                                                             jobject, jint inst,
                                                             jstring prefix,
                                                             jint types) {
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getEntries
 * Signature: (ILjava/lang/String;I)[I
 */
JNIEXPORT jintArray JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries
  (JNIEnv* env, jobject, jint inst, jstring prefix, jint types)
{
""",
        True,
    )

    # Ensure functions with overloads are handled correctly
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    setRaw
 * Signature: (IJ[BZ)Z
 */
JNIEXPORT jboolean JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_setRaw__IJ_3BZ
  (JNIEnv* env, jobject, jint entry, jlong time, jbyteArray value,
   jboolean force)
{
"""
    run_and_check_file(Jni(), "./NetworkTablesJNI.cpp", contents, contents, True)

    # Ensure text before JNIEXPORT and after args and ")" is handled correctly
    # as well as two JNI functions in a row
    run_and_check_file(
        Jni(),
        "./TestJNI.cpp",
        """/**
 *
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance
  (JNIEnv *, jobject)
{
  return nt::GetDefaultInstance();
}

JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv *, jobject)
{
  return nt::CreateInstance();
}
""",
        """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getDefaultInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance
  (JNIEnv *, jobject)
{
  return nt::GetDefaultInstance();
}

/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv *, jobject)
{
  return nt::CreateInstance();
}
""",
        True,
    )

    # Handle function declarations properly
    contents = """/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    getDefaultInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance
  (JNIEnv *, jobject);

/*
 * Class:     edu_wpi_first_networktables_NetworkTablesJNI
 * Method:    createInstance
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance
  (JNIEnv *, jobject)
{
  return nt::CreateInstance();
}
"""
    run_and_check_file(Jni(), "./TestJNI.cpp", contents, contents, True)

    # Handle functions whose arguments don't have variable names properly
    run_and_check_file(
        Jni(),
        "./DigitalGlitchFilterJNI.cpp",
        """/*
 * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI
 * Method:    cleanFilter
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter
  (JNIEnv *, jobject, jint)
{
  HAL_CleanFilter(handle);
}
""",
        """/*
 * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI
 * Method:    cleanFilter
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter
  (JNIEnv *, jobject, jint)
{
  HAL_CleanFilter(handle);
}
""",
        True,
    )
