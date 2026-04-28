.class Lio/peakmood/mobile/MainActivity$6$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity$6;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lio/peakmood/mobile/MainActivity$6;

.field final synthetic val$response:Lorg/json/JSONObject;

.field final synthetic val$status:I


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity$6;ILorg/json/JSONObject;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x1010,
            0x1010
        }
        names = {
            null,
            null,
            null
        }
    .end annotation

    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 467
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$6$1;->this$1:Lio/peakmood/mobile/MainActivity$6;

    iput p2, p0, Lio/peakmood/mobile/MainActivity$6$1;->val$status:I

    iput-object p3, p0, Lio/peakmood/mobile/MainActivity$6$1;->val$response:Lorg/json/JSONObject;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 3

    .line 470
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$6$1;->this$1:Lio/peakmood/mobile/MainActivity$6;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$6;->this$0:Lio/peakmood/mobile/MainActivity;

    iget v1, p0, Lio/peakmood/mobile/MainActivity$6$1;->val$status:I

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$6$1;->val$response:Lorg/json/JSONObject;

    invoke-static {v0, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1400(Lio/peakmood/mobile/MainActivity;ILorg/json/JSONObject;)V

    .line 471
    return-void
.end method
