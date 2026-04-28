.class Lio/peakmood/mobile/MainActivity$8$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity$8;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lio/peakmood/mobile/MainActivity$8;

.field final synthetic val$error:Ljava/lang/String;

.field final synthetic val$status:I


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity$8;ILjava/lang/String;)V
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

    .line 686
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$8$1;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iput p2, p0, Lio/peakmood/mobile/MainActivity$8$1;->val$status:I

    iput-object p3, p0, Lio/peakmood/mobile/MainActivity$8$1;->val$error:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 689
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$2302(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 690
    iget v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->val$status:I

    const/16 v1, 0x191

    if-eq v0, v1, :cond_0

    iget v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->val$status:I

    const/16 v1, 0x194

    if-ne v0, v1, :cond_1

    .line 691
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$1700(Lio/peakmood/mobile/MainActivity;)V

    .line 692
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$300(Lio/peakmood/mobile/MainActivity;)V

    .line 694
    :cond_1
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$8$1;->val$error:Ljava/lang/String;

    const-string v2, "\u0421\u0411\u041e\u0419"

    const-string v3, "\u0416\u0435\u043e\u0434\u0430 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u043d\u0430"

    invoke-static {v0, v3, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 695
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$1;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$900(Lio/peakmood/mobile/MainActivity;)V

    .line 696
    return-void
.end method
