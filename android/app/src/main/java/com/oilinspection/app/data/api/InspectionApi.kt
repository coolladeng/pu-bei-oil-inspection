package com.oilinspection.app.data.api

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query
import okhttp3.MultipartBody

interface InspectionApi {

    @GET("run-plans")
    suspend fun getRunPlans(
        @Query("month") month: String? = null,
        @Query("dept_id") deptId: Long? = null,
        @Query("status") status: Int? = null,
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 100
    ): PlanListResponse

    @GET("run-points")
    suspend fun getRunPoints(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 500
    ): PointListResponse

    @POST("run-records")
    suspend fun submitRecord(@Body record: RunRecordSubmit): RecordSubmitResponse

    @GET("run-records/today")
    suspend fun getTodayRecords(): TodayRecordResponse

    @Multipart
    @POST("uploads/photo")
    suspend fun uploadPhoto(@Part file: MultipartBody.Part): UploadResponse
    @GET("equipments")
    suspend fun getEquipments(
        @Query("page") page: Int = 1,
        @Query("pageSize") pageSize: Int = 200
    ): EquipmentListResponse

    @GET("hazards")
    suspend fun getHazards(
        @Query("page") page: Int = 1,
        @Query("pageSize") pageSize: Int = 100
    ): HazardListResponse

    @GET("auth/profile")
    suspend fun getProfile(): UserProfile

}
