.class Lio/peakmood/mobile/MainActivity$5;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->openSession()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lio/peakmood/mobile/MainActivity;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010
        }
        names = {
            null
        }
    .end annotation

    .line 345
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 349
    :try_start_0
    new-instance v0, Lorg/json/JSONObject;

    invoke-direct {v0}, Lorg/json/JSONObject;-><init>()V

    .line 350
    const-string v1, "device_id"

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v2}, Lio/peakmood/mobile/MainActivity;->access$500(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    .line 351
    const-string v1, "client_version"

    const-string v2, "1.0.0"

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    .line 352
    const-string v1, "model"

    sget-object v2, Landroid/os/Build;->MODEL:Ljava/lang/String;

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    .line 353
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    const-string v2, "/api/v1/session/open"

    const/4 v3, 0x0

    invoke-static {v1, v2, v0, v3}, Lio/peakmood/mobile/MainActivity;->access$600(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    .line 354
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    const-string v2, "session_token"

    invoke-virtual {v0, v2}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v1, v0}, Lio/peakmood/mobile/MainActivity;->access$702(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)Ljava/lang/String;

    .line 355
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    new-instance v1, Lio/peakmood/mobile/MainActivity$5$1;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$5$1;-><init>(Lio/peakmood/mobile/MainActivity$5;)V

    invoke-virtual {v0, v1}, Lio/peakmood/mobile/MainActivity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 372
    goto :goto_0

    .line 370
    :catch_0
    move-exception v0

    .line 371
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$1300(Lio/peakmood/mobile/MainActivity;)V

    .line 373
    :goto_0
    return-void
.end method
