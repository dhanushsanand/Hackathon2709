import React, { useState, type ChangeEvent } from "react";
import { Upload, FileText, Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function PdfUpload():React.JSX.Element {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (!file) return;
    setLoading(true);
    // Mock API call
    setTimeout(() => {
      setLoading(false);
      alert(`Uploaded: ${file.name}`);
    }, 2000);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-6">
      <Card className="w-full max-w-lg shadow-md">
        <CardHeader>
          <CardTitle className="text-center text-xl font-semibold">
            Upload PDF
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          <div className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-xl p-8 bg-white">
            <FileText className="h-12 w-12 text-gray-500 mb-3" />
            <p className="text-gray-600 text-center mb-4">
              Select a PDF to generate questions
            </p>

            <Label
              htmlFor="pdf-upload"
              className="w-full flex flex-col items-center justify-center"
            >
              <Input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
                id="pdf-upload"
              />
              <Button variant="outline" asChild>
                <span className="flex items-center gap-2">
                  <Upload className="h-4 w-4" /> Choose PDF
                </span>
              </Button>
            </Label>

            {file && (
              <p className="text-sm text-gray-700 mt-3">Selected: {file.name}</p>
            )}
          </div>

          <Button
            className="w-full"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" /> Uploading...
              </>
            ) : (
              "Upload and Continue"
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
